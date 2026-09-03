# 🎵 Spotify Personal Analytics

> Um dashboard pessoal, offline e interativo que processa o seu histórico completo do Spotify, calcula o tempo total de escuta e gera gráficos detalhados sobre seus hábitos musicais ao longo dos anos.

---

## 🔒 Isenção de Responsabilidade e Privacidade

Este é um projeto de uso estritamente pessoal, acadêmico e de portfólio. A análise é realizada 100% offline a partir do arquivo oficial *Extended Streaming History* exportado pelo usuário, em total conformidade com as diretrizes do Spotify e sem risco de violação de cotas (*rate limits*) da API.

---

## 📌 Sobre o Projeto

O **Spotify Personal Analytics** foi criado para quem quer ir além do resumo anual do *Spotify Wrapped* e explorar estatísticas completas de toda a sua trajetória na plataforma.

Ao invés de depender de requisições contínuas na API, a aplicação consome os dados históricos em JSON fornecidos pelo próprio Spotify. O sistema realiza o tratamento dos registros, calcula o tempo efetivo de escuta por dia, identifica seus top artistas e faixas, e consolida relatórios visuais interativos.

---

## 🚀 Funcionalidades

- ⏱️ **Contabilização Precisa do Tempo:** Processa a minutagem real escutada por dia, mês e ano.
- 📊 **Gráficos Interativos:** Exibe visualizações dinâmicas com os artistas mais ouvidos, histórico de faixas e comportamento de escuta.
- ⏭️ **Análise de Disposição (Skip Rate):** Identifica a quantidade e porcentagem de músicas que foram puladas antes do fim.
- 🕒 **Mapeamento de Horários (Heatmap):** Mostra os dias da semana e horários de maior consumo de áudio.
- 💾 **Persistência Local (Opcional):** Estruturação dos dados em banco SQLite/PostgreSQL para consultas SQL customizadas.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Processamento de Dados:** Pandas / NumPy
- **Visualização:** Plotly / Matplotlib / Seaborn
- **Dashboard Interativo:** Streamlit
- **Banco de Dados:** SQLite

---

## 🔧 Estrutura do Sistema

1. **Extração:** Consumo do histórico estendido (`Streaming_History_Audio_*.json`).
2. **Tratamento (ETL):** Conversão de milissegundos em minutos/horas, unificação de arquivos e limpeza de dados via Pandas.
3. **Persistência:** Modelagem relacional das reproduções em SQLite para consultas SQL de alta performance.
4. **Visualização:** Renderização do dashboard web local com métricas e filtros temporais usando Streamlit.

---

## 📥 Como Obter Seus Dados

1. Acesse a página de privacidade da sua conta no Spotify: [spotify.com/account/privacy](https://www.spotify.com/account/privacy/).
2. Na seção **Download dos seus dados**, marque a opção **Histórico de reprodução estendido**.
3. Confirme o pedido no seu e-mail e aguarde o envio do arquivo compactado pelo Spotify.

---

## 💻 Como Executar

### 1. Clonar o repositório
```bash
git clone [https://github.com/seu-usuario/spotify-personal-analytics.git](https://github.com/seu-usuario/spotify-personal-analytics.git)
cd spotify-personal-analytics
