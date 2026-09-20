### Pergunta: os plays muito curtos distorcem as minhas métricas?

**Consulta:** distribuição de plays e horas por faixa de duração (`sql/consultas.sql`)

**Resultado:** 47,4% dos plays duram menos de 30s, mas representam só 3,0% das horas
(132 de 4.409 h). Plays de mais de 2 min são 35,3% dos plays e 80,9% das horas.

**Conclusão:** o total de horas escutadas é robusto (−3% ao filtrar), mas as contagens
de plays, artistas e faixas ficam infladas por plays de poucos segundos.
Decisão: definir "play válido" como ≥ 30s (mesmo critério do Spotify para contar um
stream) nas análises de contagem, e manter as horas sem filtro.