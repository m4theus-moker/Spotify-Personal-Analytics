import streamlit as st
import analises as an

st.set_page_config(page_title="Spotify Personal Analytics",
                   page_icon="🎵", layout="wide")


@st.cache_data
def carregar():
    return an.carregar_dados("data/spotify.db")


df = carregar()

st.title("🎵 Spotify Personal Analytics")

# Filtros na barra lateral
st.sidebar.header("Filtros")
anos = sorted(df['ano'].unique())
anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)
top_n = st.sidebar.slider("Quantidade no ranking", 5, 30, 15)
min_plays = st.sidebar.slider("Mínimo de plays (skip rate)", 10, 200, 50)

df_f = df[df['ano'].isin(anos_sel)]
if df_f.empty:
    st.warning("Selecione pelo menos um ano.")
    st.stop()

# Métricas
c1, c2, c3, c4 = st.columns(4)
c1.metric("Horas escutadas", f"{df_f['min_played'].sum() / 60:,.0f}h")
c2.metric("Artistas diferentes", f"{df_f['artista'].nunique():,}")
c3.metric("Faixas diferentes", f"{df_f['faixa'].nunique():,}")
c4.metric("Taxa de skip", f"{df_f['pulada'].mean() * 100:.1f}%")

# Abas
aba1, aba2, aba3 = st.tabs(["Visão geral", "Artistas e faixas", "Hábitos"])

with aba1:
    st.plotly_chart(an.horas_por_ano(df))

with aba2:
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(an.top_artistas(df_f, top_n))
    col_b.plotly_chart(an.top_faixas(df_f, top_n))
    st.plotly_chart(an.skip_rate(df_f, min_plays, top_n))

with aba3:
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(an.por_hora(df_f))
    col_b.plotly_chart(an.por_dia_semana(df_f))