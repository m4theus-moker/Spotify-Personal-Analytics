SELECT CASE WHEN ms_played < 30000 THEN '1. < 30s'
            WHEN ms_played < 120000 THEN '2. 30s-2min'
            ELSE '3. > 2min' END AS duracao,
       COUNT(*) AS plays,
       ROUND(SUM(min_played) / 60, 1) AS horas
FROM streams
GROUP BY 1
ORDER BY 1;