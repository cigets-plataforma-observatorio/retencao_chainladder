-- Carregar tabela de municipios com informações sobre UF, Região de Saúde, Nomes etc
-- Coletar os dados sobre os municípios

SELECT
    uf,
    uf_sigla,
    cod_regsaud,
    regiao_saude,
    cod_municipiodv,
    CAST(cod_municipio AS VARCHAR) AS cod_municipio,
    municipio
FROM "Analytics Layer".Territorial."Municípios - Hierarquia Completa" m
         LEFT JOIN Dados.territorial."tb_municip.parquet" m2 on m.cod_municipio = m2.CO_MUNICIP