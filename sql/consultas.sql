   SELECT COUNT(*) AS plays,
          COUNT(DISTINCT artista) AS artistas,
          COUNT(DISTINCT faixa) AS faixas,
          MIN(ts) AS primeiro_play,
          MAX(ts) AS ultimo_play,
          ROUND(SUM(min_played) / 60, 1) AS horas_totais
   FROM streams;