from operator import attrgetter
import pandas as pd
from datetime import datetime


def calcular_saida(row):
    old_values = row.copy()
    for col in row.index:
        try:
            if col == 180:
                row[col] = None
            else:
                if col < 12:
                    row[col] = row[col] - old_values[col + 12]
                else:
                    row[col] = (row[col] - old_values[col + 12]) + row[col - 12]
        except:
            pass
    return row


def gerar_triangulo(df):
    saidas = pd.melt(df.copy().apply(calcular_saida, axis=1).reset_index().drop([180], axis=1),
                     id_vars=['cohort'], value_name='values', var_name='period_number').sort_values(
        ["cohort", 'period_number'])
    saidas['origin'] = saidas['cohort'].dt.year
    saidas['development'] = (saidas['cohort'] + saidas['period_number'])
    saidas['development'] = saidas['development'].apply(lambda x: datetime.strptime(str(x), '%Y-%m').year)
    saidas['dif'] = saidas['development'] - saidas['origin']
    saidas.sort_values(['dif', 'origin'], inplace=True)
    saidas = saidas[['development', 'origin', 'values']]
    saidas.dropna(inplace=True)

    return saidas


def gerar_triangulo_agregado(df_tmp):
    # Converter a coluna competência para o formato ANO-MES (datetime)
    df_tmp['COMPETEN'] = pd.to_datetime(df_tmp['COMPETEN'], format='%Y%m').dt.to_period('M')

    # Criar o grupo no qual o profissional pertence (sua primeira competência)
    df_tmp['cohort'] = df_tmp.groupby('CPF_PROF')['COMPETEN'].transform('min')

    # Contar a quantidade de profissionais distintos por CPF para cada grupo e competência
    df_cohort = df_tmp.groupby(['uf_sigla', 'cod_regsaud', 'cohort', 'COMPETEN']).agg(
        n_prof=('CPF_PROF', 'nunique')).reset_index(drop=False)

    # Eliminar o primeiro grupo
    df_cohort = df_cohort[df_cohort['cohort'] != '2008-01']

    # Calcular a diferença em meses entre a competência e o grupo (primeira competência)
    df_cohort['period_number'] = (df_cohort.COMPETEN - df_cohort.cohort).apply(attrgetter('n'))

    # Realizar pivot da tabela
    cohort_pivot = df_cohort.pivot_table(index=['cohort'], columns='period_number', values='n_prof')

    # Obter o tamanho de cada grupo (cohort)
    cohort_size = cohort_pivot.iloc[:, 0]

    return cohort_pivot, cohort_size


def gerar_ml_features(retention_matrix, regiao_saude):
    obs = retention_matrix.describe().drop(0, axis=1).drop(['count']).stack().to_frame().T
    obs.columns = ['_'.join([str(c) for c in col]) for col in obs.columns.values]
    obs['cod_regsaud'] = regiao_saude
    obs = obs.set_index('cod_regsaud')
    return obs


def calcular_restantes(cl_model, cohort_pivot):
    """
    O modelo chainladder calcula a quantidade de profissionais que saíram por mês.
    Essa função calcula, a partir do número inicial, quantos restaram, por meio de subtração
    :param cl_model:
    :param cohort_pivot:
    :return:
    """
    dados = cl_model.full_triangle_.to_frame()

    dados.drop([192, 9999], axis=1, inplace=True)
    dados.index = dados.index.strftime('%Y-%m')
    dados[0] = cohort_pivot[0].values[:-1]
    for col in dados.columns:
        if col != 0:
            dados[col] = (round(dados[0] - dados[col]))  # as typeint
        else:
            dados[col] = dados[col]  # astypeint
    dados = dados[[0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180]]
    return dados


def calcular_percentual_restantes(restantes, cohort_size):
    return restantes.divide(cohort_size.values[:-1], axis=0)


def calcular_retencao_ano_regiao(percentual_restantes, regiao_saude):
    aux = percentual_restantes.melt(var_name='periodo', value_name='retention', ignore_index=False).reset_index().rename(
        columns={'index': 'cohort'})
    aux['cohort'] = pd.to_datetime(aux['cohort'])
    aux['a'] = aux.apply(lambda row: row['cohort'] + pd.DateOffset(months=row['periodo']), axis=1)
    aux2 = aux.loc[(aux['a'] <= '2024-01-01') & (aux['periodo'] != 0)].groupby('a').head(5)  # Considera os últimos 5 (diagonal)
    aux2 = aux2.loc[aux['a'] >= '2014-01-01']
    aux2['a'] = aux2['a'].dt.strftime('%Y-%m')
    aux2 = aux2.groupby('a')[['retention']].mean().reset_index().rename(columns={'a': 'ano'})
    aux2['regiao_saude'] = regiao_saude
    return aux2


def pre_processar_dados_retencao(percentual_restantes):
    df = percentual_restantes.reset_index().melt(id_vars='index')
    df['periodo'] = pd.to_datetime(df['index'], format='%Y-%m').dt.to_period('M') + df['variable'].astype(int).apply(
        pd.offsets.MonthEnd)
    df['is_predicted'] = df['periodo'] > '2024-01'
    df = df.set_index(['variable', 'index'])

    # select pandas rows where periodo is max in each 'index' group and is_predicted is False
    reais = df[(df['is_predicted'] == False)]
    preditos = reais.loc[reais.groupby('index')['periodo'].idxmax()]
    preditos['is_predicted'] = True

    df = pd.concat([df, preditos]).sort_values(['index', 'variable'])
    return df
