# 🎵 Spotify Daily Analytics

> Um dashboard pessoal e automatizado que rastreia seus hábitos de escuta no Spotify, calcula o tempo total ouvido no dia e gera gráficos interativos com a distribuição dos seus gêneros musicais preferidos.

---

## 📌 Sobre o Projeto

O **Spotify Daily Analytics** foi criado para quem quer ir além do *Spotify Wrapped* anual e acompanhar suas estatísticas de música **diariamente**. 

Através da API Web do Spotify, a aplicação faz o monitoramento em tempo real do que você está ouvindo, acumula o tempo de reprodução por faixa, mapeia os gêneros de cada artista e consolida relatórios diários com gráficos.

---

## 🚀 Funcionalidades

- ⏱️ **Contabilização de Tempo Real:** Monitora execuções ativas e registra quantos minutos/horas foram ouvidos ao longo do dia.
- 🎨 **Mapeamento e Agrupamento de Gêneros:** Normaliza subgêneros específicos em categorias abrangentes para evitar gráficos poluídos.
- 📊 **Gráficos Diários:** Gera visuais (pizza/rosca e barras) com a porcentagem de cada gênero e os artistas mais escutados.
- 💾 **Histórico Local:** Persistência em banco de dados leve (SQLite) para consultas históricas.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **API:** [Spotify Web API](https://developer.spotify.com/documentation/web-api/) via [Spotipy](https://spotipy.readthedocs.io/)
- **Processamento de Dados:** Pandas / NumPy
- **Visualização:** Matplotlib / Seaborn
- **Banco de Dados:** SQLite

---

## 🔧 Estrutura do Sistema

1. **Daemon / Scheduler:** Consulta periodicamente o endpoint `/me/player/currently-playing`.
2. **Normalizador:** Extrai as tags de gênero do artista e classifica em categorias macro.
3. **Persistência:** Salva as faixas, durações e carimbos de data/hora (*timestamps*).
4. **Relatório Diário:** Um script gera o gráfico final do dia e estatísticas resumidas.

---

## 🤝 Contribuição

Contribuições são super bem-vindas! Sinta-se à vontade para abrir uma *Issue* com sugestões de melhorias ou enviar um *Pull Request*.
