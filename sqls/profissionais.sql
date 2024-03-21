-- Coletar os dados sobre os profissionais
-- Coletar competencia, código do município e CPF do profissional do CNES-PF de forma distinta.
-- Ou seja, busca-se encontrar para cada ano e cada profissional, uma linha para cada município onde ele atuou. Entende-se o 'ano' como a competência 01 (janeiro).
-- Nesse primeiro momento a análise está limitada apenas aos profissionais médicos e enfermeiros

SELECT DISTINCT
    COMPETEN,
    CODUFMUN,
    CASE
        WHEN pf.CBO LIKE '225%' OR pf.CBO LIKE '2231%' THEN 'Médico'
        WHEN pf.CBO LIKE '2235%' THEN 'Enfermeiro'
        END AS categoria,
    CPF_PROF
FROM Dados.cnes.PF
WHERE
        SUBSTR(COMPETEN, 1, 4) >= 2006
  AND SUBSTR(COMPETEN, 5, 2) = '01'
  AND (
        (pf.CBO LIKE '225%' OR pf.CBO LIKE '2231%') OR -- Medico
        (pf.CBO LIKE '2235%') -- Enfermeiro
    )