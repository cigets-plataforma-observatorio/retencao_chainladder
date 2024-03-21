import matplotlib.pyplot as plt
import seaborn as sns
from tratamentos import pre_processar_dados_retencao
from avaliacao import calcular_mape


def generate_retention_curve(dataframe, ax):
    not_predicted = dataframe.loc[dataframe['is_predicted'] == False].unstack()
    not_predicted.columns = not_predicted.columns.droplevel()
    not_predicted.plot(cmap='tab20', ax=ax)

    predicted = dataframe.loc[dataframe['is_predicted'] == True].unstack()
    predicted.columns = predicted.columns.droplevel()
    predicted.plot(ls='--', cmap='tab20', ax=ax)

    ax.legend(ncol=5)
    ax.set_ylim(0, 1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_title('Retenção percentual por período e cohort')
    ax.set_xlabel('períodos (meses)')


def generate_mape_boxplot(triangle_model, ax):
    mape = calcular_mape(triangle_model)
    mape.plot.box(ax=ax)
    ax.set_ylim(0, 1)
    ax.set_title('MAPE por período')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('períodos (meses)')


def generate_retention_matrix(dataframe, ax, percentual):
    if percentual:
        fmt = '.0%'
        titulo = 'percentual'
    else:
        fmt = 'g'
        titulo = 'absoluta'

    sns.heatmap(dataframe,
                mask=dataframe.isnull(),
                annot=True,
                fmt=fmt,
                annot_kws={"size": 8},
                cmap='RdYlGn',
                ax=ax)

    ax.set(xlabel='períodos (meses)', ylabel='')
    for linha in range(1, len(dataframe)+1):
        minimo = dataframe.shape[1]-linha
        ax.hlines(y=linha, xmin=minimo, xmax=minimo+1, color='white', linewidth=2)
        ax.vlines(x=linha, ymin=minimo, ymax=minimo+1, color='white', linewidth=2)

    ax.set_title(f'Retenção {titulo} por período e cohort')

    t = ax.text(4, 4, 'Real', color='white', fontsize=18, ha='center')
    t.set_bbox(dict(facecolor='black', alpha=0.25, edgecolor='white'))

    t2 = ax.text(11, 11, 'Predito', color='white', fontsize=18, ha='center')
    t2.set_bbox(dict(facecolor='black', alpha=0.25, edgecolor='white'))


def gerar_graficos(restantes, percentual_restantes, cl_model, titulo, nome_arquivo):
    # Plotar o gráfico
    fig, ax = plt.subplots(2, 2, figsize=(15, 10), gridspec_kw={'width_ratios': [6, 6]})

    # Matriz de Retenção com números absolutos
    generate_retention_matrix(dataframe=restantes.copy(), ax=ax[0][0], percentual=False)

    # Matriz de Retenção com números percentuais
    generate_retention_matrix(dataframe=percentual_restantes.copy(), ax=ax[0][1], percentual=True)

    # Curva de Retenção percentual com real e preditos
    dados_retencao = pre_processar_dados_retencao(percentual_restantes.copy())
    generate_retention_curve(dataframe=dados_retencao.copy(), ax=ax[1][0])

    # Boxplot mape
    generate_mape_boxplot(triangle_model=cl_model, ax=ax[1][1])

    plt.suptitle(titulo, fontsize=16)
    fig.tight_layout()
    plt.savefig(f'./imgs/{nome_arquivo}.png')
    plt.close()
