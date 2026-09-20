# Análise do meu histórico do Spotify

Perguntas respondidas em SQL sobre o `spotify.db` (Extended Streaming History, de 09/08/2023 a 03/09/2026). As consultas estão em [`sql/consultas.sql`](sql/consultas.sql).

**Visão geral dos dados:** 195.785 plays, 4.408,9 horas, 5.354 artistas e 14.841 faixas. Isso dá uma média de ~3,9 h de escuta por dia e de apenas ~81 segundos por play, número que a primeira pergunta ajuda a explicar.

---

### 1. Os plays muito curtos distorcem as minhas métricas?

**Consulta:** distribuição de plays e horas por faixa de duração.

**Resultado:**

| Duração do play | Plays | % dos plays | Horas | % das horas |
|---|---|---|---|---|
| Menos de 30 s | 92.757 | 47,4% | 132,2 | 3,0% |
| De 30 s a 2 min | 33.986 | 17,4% | 711,0 | 16,1% |
| Mais de 2 min | 69.042 | 35,3% | 3.565,7 | 80,9% |

**Conclusão:** quase metade dos plays dura menos de 30 s (em média ~5 s), mas isso representa só 3% do tempo escutado. O total de horas é robusto (−3% ao filtrar), mas as contagens de plays, artistas e faixas ficam infladas por plays de poucos segundos. Decisão: definir "play válido" como ≥ 30 s (mesmo critério do Spotify para contar um stream) nas análises de contagem, e manter as horas sem filtro.

---

### 2. Como terminam os meus plays, e como a coluna `pulada` foi definida?

**Consulta:** contagem de plays e duração média por `reason_end`, comparada com a coluna `pulada` e com a flag `skipped` original do Spotify.

**Resultado:**
- `trackdone` (foi até o fim): 66.334 plays (33,9%), média de 176 s.
- `fwdbtn` (botão de próxima): 76.310 plays (39,0%), média de 31 s.
- `endplay`: 41.891 plays (21,4%), média de 31 s.
- `backbtn` (botão de voltar): 4.903 plays (2,5%), média de 8 s.
- Os demais motivos somam menos de 3% dos plays.
- A coluna `pulada` coincide exatamente com o `skipped` do Spotify: os três motivos `fwdbtn`, `endplay` e `backbtn` (123.104 plays, 62,9%) são os únicos marcados como skip.

**Conclusão:** só um terço das faixas é ouvido até o fim. A taxa de skip de 62,9% segue a definição do Spotify, que inclui `endplay` e o botão de voltar; considerando só o botão de próxima, seria 39,0%. Decisão: manter a definição do Spotify e documentá-la, e usar "ouvida até o fim" (33,9%) como métrica complementar, que não depende dessa definição.

---

### 3. Como a minha escuta evoluiu mês a mês?

**Consulta:** horas por mês com variação em relação ao mês anterior (`LAG`), e depois horas por dia para corrigir meses incompletos.

**Resultado:** média de ~120 h/mês (~4 h/dia) nos 36 meses completos, sem tendência de alta ou queda: 129 h/mês em 2024, 118 em 2025 e 117 em 2026 (jan a ago). O maior mês foi fev/2025 (187,0 h) e o menor, set/2025 (59,9 h), que veio depois de quatro meses seguidos abaixo de 80 h. Em out/2025 a escuta mais que dobrou (133,8 h). Em ago/2026 houve outro pico (170,2 h).

**Conclusão:** o hábito de escuta é estável, com variação mensal de até 3x. Os meses das pontas (ago/2023, que começa no dia 9, e set/2026, que termina no dia 3) são incompletos, então a comparação entre anos só é válida por horas por dia. O mesmo vale para o gráfico "horas por ano" do dashboard, porque 2023 e 2026 são anos parciais.

---

### 4. Eu sou fiel a um artista ou troco o tempo todo?

**Consulta:** artista nº 1 de cada mês, com sua participação nas horas do mês (`RANK` e `SUM() OVER`).

**Resultado:** o VMZ foi o nº 1 em 32 dos 38 meses (84%). Os outros líderes foram Eminem (nov/2024), kamaitachi (set/2025), Slipknot (out/2025) e Alec' (abr, jun e set/2026). O pico foi jan/2025, com 72,8 h de VMZ (40,4% do mês). A participação média do artista líder caiu de ~26% (2023) e ~17% (2024) para ~11% em 2026.

**Conclusão:** o hábito é de um artista dominante, e os meses de maior escuta (jan e fev de 2025) coincidem com picos dele. Em 2026 a escuta ficou mais diversa, com Alec' liderando três meses. O mês de menor escuta (set/2025) também foi o mais fragmentado, com o líder em apenas 7,5%.

---

### 5. Quanto do meu tempo de escuta se concentra em poucos artistas?

**Consulta:** participação de cada artista nas horas totais.

**Resultado:** o VMZ soma 767,5 h (17,4% das 4.408,9 h), 7,6 vezes o segundo colocado (kamaitachi, com 100,9 h). O top 10 concentra 30,8% das horas; sem o VMZ, o top 9 soma só 13,4%. Os outros ~5.340 artistas dividem os 69,2% restantes.

**Conclusão:** escuta com um artista dominante e uma cauda muito longa. O ranking total difere do mensal: kamaitachi e Slipknot são o 2º e o 3º no total, mas raramente lideram um mês, o que indica uma escuta constante e sem picos.

---

## Limitações e cuidados

- O histórico começa em 09/08/2023 e termina em 03/09/2026, então o primeiro e o último mês são incompletos.
- Registros sem faixa associada (como podcasts) foram removidos no tratamento, e por isso não entram nos totais.
- A coluna `artista` vem do artista do álbum no export do Spotify, então faixas com participação especial são atribuídas ao artista principal do álbum.
- A definição de skip é a do Spotify (inclui o botão de voltar e o `endplay`).

## Próximas perguntas

- Quantos artistas novos eu descubro por mês (considerando só plays válidos, de 30 s ou mais)?
- Como são as minhas sessões de escuta (duração, horário, maratonas)?
- O skip rate muda por hora do dia, por dia da semana ou no modo shuffle?