# 🎵 Spotify Personal Analytics

> Um pipeline pessoal, 100% offline, que processa o histórico completo de streaming do Spotify (Extended Streaming History) e transforma os dados brutos em análises visuais sobre hábitos de escuta.

---

## 📌 Sobre o Projeto

Em vez de depender do resumo anual do *Spotify Wrapped* ou de requisições contínuas à API oficial (com risco de *rate limit*), este projeto consome diretamente o arquivo de **Extended Streaming History**, exportado pelo próprio usuário através da página de privacidade do Spotify.

O objetivo é extrair, tratar e visualizar o histórico de reprodução para responder perguntas como: quanto tempo eu realmente escuto música por ano/mês? Quais artistas e faixas dominam minha rotina? Em que horários e dias eu mais escuto?

---

## 📸 Prévia

![Dashboard](imagens/dashboard.png)

---

## 📊 O que os dados mostraram

- **47,4%** dos plays duram menos de 30 s, mas representam só **3%** das horas escutadas.
- Só **33,9%** das faixas são ouvidas até o fim.
- O artista mais ouvido concentra **17,4%** das 4.408,9 horas e foi o nº 1 em **32 dos 38 meses**.

Detalhes, consultas e conclusões em [analise.md](analise.md).

---

## 🚀 Funcionalidades Implementadas

- 📂 **Extração automatizada:** leitura e unificação de todos os arquivos `Streaming_History_Audio_*.json` do export, mesmo quando divididos em múltiplos arquivos.
- 🧹 **Tratamento de dados (ETL):** conversão de timestamps de UTC para `America/Sao_Paulo`, cálculo de minutos efetivos de escuta (a partir de `ms_played`), remoção de registros sem faixa associada (ex: podcasts) e geração de colunas auxiliares de tempo (ano, mês, dia da semana, hora).
- 📊 **Visualização:** gráfico de pizza interativo (Plotly) mostrando a distribuição de minutos escutados por ano.
- 🏆 **Top artistas e faixas:** gráficos de barras com os artistas e as faixas mais escutados (em horas/minutos).
- ⏭️ **Análise de skip rate:** artistas mais pulados, com base no campo `skipped` do Spotify (que inclui o botão de próxima, o `endplay` e o botão de voltar) e com mínimo de plays configurável para evitar distorções.
- 🕐 **Escuta por hora e dia da semana:** gráficos de barras mostrando em quais horas do dia e em quais dias da semana a escuta se concentra.
- 🗄️ **Persistência em SQLite:** histórico tratado em `spotify.db` (tabelas `streams` e `resumo_artistas`) para consultas em SQL.
- 🔎 **Análises em SQL:** perguntas respondidas com CTEs e funções de janela (`LAG`, `RANK`), documentadas em [analise.md](analise.md).
- 🖥️ **Dashboard interativo (Streamlit):** filtros por ano, rankings configuráveis e abas com visão geral, artistas/faixas e hábitos de escuta.
- 💾 **Exportação:** geração de um CSV tratado (`spotify_tratado.csv`), pronto para ser consumido em ferramentas de BI como Power BI.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3
- **Processamento de dados:** Pandas
- **Banco de dados:** SQLite
- **Visualização:** Plotly Express
- **Dashboard:** Streamlit
- **Ambiente de desenvolvimento:** Google Colab (ETL e exploração) e VS Code (dashboard e SQL)

---

## 🔧 Estrutura do Pipeline

1. **Upload e extração** do arquivo `.zip` do Extended Streaming History diretamente no Colab.
2. **Leitura** de todos os arquivos JSON (`Streaming_History_Audio_*.json`) e unificação em um único DataFrame.
3. **Tratamento:**
   - Conversão de `ts` para datetime, com fuso `America/Sao_Paulo`
   - Conversão de `ms_played` para minutos
   - Seleção das colunas relevantes (faixa, artista, álbum, tempo de escuta, motivo de término, se foi pulada, se estava em shuffle)
   - Remoção de registros inválidos
   - Criação de colunas de ano, mês, dia da semana e hora
   - Criação da coluna `pulada` (combinando `skipped` e `reason_end == 'fwdbtn'`)
4. **Visualização** dos minutos escutados por ano em gráfico de pizza.
5. **Análises:** top artistas, top faixas e skip rate por artista.
6. **Persistência** em banco SQLite (`spotify.db`) com a tabela completa e um resumo agregado por artista.
7. **Exportação** para CSV, com encoding compatível (`utf-8-sig`) para uso direto no Power BI ou Excel.

---

## 📥 Como Obter os Dados

1. Acesse [spotify.com/account/privacy](https://www.spotify.com/account/privacy/).
2. Na seção "Download dos seus dados", solicite o **Histórico de reprodução estendido** (Extended Streaming History).
3. Aguarde o e-mail do Spotify com o arquivo compactado (pode levar até 30 dias).

---

## 💻 Como Executar

### 1. Gerar o banco de dados (notebook)

1. Abra o notebook no Google Colab.
2. Rode a célula de upload e selecione o `.zip` recebido do Spotify.
3. Execute as células em sequência (extração → tratamento → visualização → persistência → exportação).
4. Baixe os arquivos gerados: `spotify.db` e `spotify_tratado.csv`.

### 2. Rodar o dashboard local

1. Coloque o `spotify.db` na pasta `data/` do projeto (ela não vai para o GitHub, porque contém dados pessoais).
2. Instale as dependências: `pip install -r requirements.txt`
3. Inicie o dashboard: `python -m streamlit run app.py`

---

## 🗂️ Estrutura do Repositório

- `app.py`: interface do dashboard em Streamlit
- `analises.py`: funções que geram cada gráfico
- `sql/consultas.sql`: consultas SQL usadas na análise
- `analise.md`: perguntas, resultados e conclusões
- `spotify_personal_analytics.py`: código do notebook (ETL)
- `requirements.txt`: dependências do projeto

---

## 🔭 Próximos Passos

- [x] Gráficos de top artistas e top faixas
- [x] Análise de taxa de músicas puladas (*skip rate*)
- [x] Gráficos de escuta por hora do dia e dia da semana
- [x] Persistência em banco SQLite para consultas SQL
- [x] Dashboard interativo com Streamlit
- [x] Análises em SQL documentadas
- [ ] ETL em camadas (arquitetura medalhão: bronze, silver e gold) em um `etl.py` local
- [ ] Dashboard: filtro de plays válidos (30 s ou mais) e métrica de faixas ouvidas até o fim
- [ ] Exportações agregadas (por mês, por artista) e dashboard no Power BI

---

## ⚠️ Nota sobre Privacidade

Este projeto é de uso estritamente pessoal, acadêmico e de portfólio. Todo o processamento é feito localmente/offline a partir de um arquivo exportado pelo próprio usuário, sem qualquer chamada à API do Spotify — em total conformidade com as diretrizes de uso de dados da plataforma. O banco de dados e os arquivos do export ficam fora do repositório.
