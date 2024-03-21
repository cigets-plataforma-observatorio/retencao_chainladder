import os
import pandas as pd
import pyodbc
from dotenv import load_dotenv


# Definir a conexão com o Dremio
def get_dremio_connection():
    """
    Obter os dados de conexão das variáveis de ambiente e estabelecer a conexão
    Deve existir um arquivo .env com conteúdo no formato:
    DREMIO_DRIVER=Dremio Connector
    DREMIO_HOST=datalake.face.ufg.br
    DREMIO_PORT=31010
    DREMIO_USER=*********
    DREMIO_PASSWORD=*******

    :return: pyodbc connection
    """

    load_dotenv('.env', override=True)

    host = os.getenv("DREMIO_HOST")
    port = os.getenv("DREMIO_PORT")
    user = os.getenv("DREMIO_USER")
    password = os.getenv("DREMIO_PASSWORD")
    driver = os.getenv("DREMIO_DRIVER")
    connection_string = f"Driver={driver};" \
                        f"ConnectionType=Direct;" \
                        f"HOST={host};" \
                        f"PORT={port};" \
                        f"AuthenticationType=Plain;" \
                        f"UID={user};" \
                        f"PWD={password}"

    return pyodbc.connect(connection_string, autocommit=True, encoding='utf8')


def obter_dados(arquivo_sql):
    with open(f'sqls/{arquivo_sql}', 'r', encoding='utf-8') as f:
        sql = f.read()

    df = pd.read_sql(sql, get_dremio_connection())
    return df
