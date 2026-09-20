   -- Temos uma consulta onde retornamos o total de plays, artistas distintos, faixas distintas, a data do primeiro play,
   -- a data do último play e o total de horas tocadas (somando o tempo de cada faixa tocada e convertendo para horas).
   SELECT COUNT(*) AS plays,
          COUNT(DISTINCT artista) AS artistas,
          COUNT(DISTINCT faixa) AS faixas,
          MIN(ts) AS primeiro_play,
          MAX(ts) AS ultimo_play,
          ROUND(SUM(min_played) / 60, 1) AS horas_totais
   FROM streams;

   -- logo abaixo temos a consulta que calcula a porcentagem de plays com duração menor que 30 segundos e a porcentagem de
   -- plays pulados (pulada = 1). A consulta retorna os resultados arredondados para uma casa decimal.
   SELECT ROUND(100.0 * SUM(ms_played < 30000) / COUNT(*), 1) AS pct_menos_30s,
       ROUND(100.0 * SUM(pulada) / COUNT(*), 1) AS pct_puladas
FROM streams;

-- Neste código, estou fazendo uma consulta que agrupa os plays por duração em três categorias: menos de 30 segundos, 
-- de 30 segundos a 2 minutos e mais de 2 minutos. Para cada categoria, estou calculando o total de plays e o total de
-- horas tocadas (somando o tempo de cada faixa tocada e convertendo para horas). A consulta retorna os resultados ordenados
-- pela categoria de duração.
SELECT CASE WHEN ms_played < 30000 THEN '1. menos de 30s'
            WHEN ms_played < 120000 THEN '2. de 30s a 2min'
            ELSE '3. mais de 2min' END AS duracao,
       COUNT(*) AS plays,
       ROUND(SUM(min_played) / 60, 1) AS horas
FROM streams
GROUP BY 1
ORDER BY 1;

-- logo nesse código, estamos agrupando os plays por motivo de término (reason_end) e calculando o total de plays e a média
-- de tempo tocado em segundos para cada motivo. A consulta retorna os resultados ordenados pelo número de plays em ordem
-- decrescente.
SELECT reason_end,
       COUNT(*) AS plays,
       ROUND(AVG(ms_played) / 1000.0, 1) AS seg_medios
FROM streams
GROUP BY reason_end
ORDER BY plays DESC;

-- Neste código, estamos agrupando os plays por motivo de término (reason_end) e calculando o total de plays,
-- o total de plays puladas e o total de plays puladas.
SELECT reason_end,
       COUNT(*) AS plays,
       SUM(pulada) AS puladas,
       SUM(CASE WHEN skipped = 1 THEN 1 ELSE 0 END) AS flag_skipped
FROM streams
GROUP BY reason_end
ORDER BY plays DESC;

-- Evolução mensal das horas escutadas, com variação em relação ao mês anterior
-- Horas por dia em cada mês (corrige o efeito de meses incompletos)
-- Artista mais ouvido de cada mês e sua participação nas horas do mês
WITH por_artista AS (
    SELECT ano, mes, artista, SUM(min_played) / 60 AS horas
    FROM streams
    GROUP BY ano, mes, artista
),
com_ranking AS (
    SELECT *,
           RANK() OVER (PARTITION BY ano, mes ORDER BY horas DESC) AS pos,
           SUM(horas) OVER (PARTITION BY ano, mes) AS horas_mes
    FROM por_artista
)
SELECT ano, mes, artista,
       ROUND(horas, 1) AS horas,
       ROUND(100.0 * horas / horas_mes, 1) AS pct_do_mes
FROM com_ranking
WHERE pos = 1
ORDER BY ano, mes;

-- Participação de cada artista no total de horas
SELECT artista,
       ROUND(SUM(min_played) / 60, 1) AS horas,
       ROUND(100.0 * SUM(min_played) / (SELECT SUM(min_played) FROM streams), 1) AS pct_total
FROM streams
GROUP BY artista
ORDER BY horas DESC
LIMIT 10;
