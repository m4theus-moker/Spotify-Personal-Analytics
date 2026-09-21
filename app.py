import streamlit as st
import analises as an

st.set_page_config(page_title="Spotify Personal Analytics",
                   page_icon="🎵", layout="wide")


@st.cache_data
def carregar():
    return an.carregar_dados("data/spotify.db")


st.title("🎵 Spotify Personal Analytics")

try:
    dados = carregar()
except FileNotFoundError:
    st.error(
        "Banco `data/spotify.db` não encontrado. Gere-o com "
        "`python etl.py \"data/arquivo.zip\"` e recarregue a página."
    )
    st.stop()
except ValueError as e:
    st.error(str(e))
    st.stop()

df = dados['streams']

# Filtros na barra lateral
st.sidebar.header("Filtros")
anos = sorted(df['ano'].unique())
anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)
top_n = st.sidebar.slider("Quantidade no ranking", 5, 30, 15)
min_plays = st.sidebar.slider("Mínimo de plays (skip rate)", 10, 200, 50)
so_validos = st.sidebar.checkbox(
    "Ignorar plays de menos de 30s",
    help="Afeta contagens e rankings de artistas/faixas. As horas não mudam "
         "muito (esses plays somam só ~3% do tempo)."
)

df_f = df[df['ano'].isin(anos_sel)]
if so_validos:
    df_f = df_f[df_f['play_valido'] == 1]
if df_f.empty:
    st.warning("Selecione pelo menos um ano.")
    st.stop()

mensal_f = dados['mensal'][dados['mensal']['ano'].isin(anos_sel)]
artista_mes_f = dados['artista_mes'][dados['artista_mes']['ano'].isin(anos_sel)]

# Métricas
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Horas escutadas", f"{df_f['min_played'].sum() / 60:,.0f}h")
c2.metric("Artistas diferentes", f"{df_f['artista'].nunique():,}")
c3.metric("Faixas diferentes", f"{df_f['faixa'].nunique():,}")
c4.metric("Taxa de skip", f"{df_f['pulada'].mean() * 100:.1f}%")
c5.metric("Ouvidas até o fim", f"{df_f['ouvida_ate_o_fim'].mean() * 100:.1f}%")

# Abas
aba1, aba2, aba3 = st.tabs(["Visão geral", "Artistas e faixas", "Hábitos"])

with aba1:
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(an.distribuicao_duracao(df_f), use_container_width=True)
    col_b.plotly_chart(an.evolucao_mensal(mensal_f), use_container_width=True)
    st.plotly_chart(an.artista_do_mes(artista_mes_f), use_container_width=True)

with aba2:
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(an.top_artistas(df_f, top_n), use_container_width=True)
    col_b.plotly_chart(an.top_faixas(df_f, top_n), use_container_width=True)
    st.plotly_chart(an.skip_rate(df_f, min_plays, top_n), use_container_width=True)

with aba3:
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(an.por_hora(df_f), use_container_width=True)
    col_b.plotly_chart(an.por_dia_semana(df_f), use_container_width=True)
