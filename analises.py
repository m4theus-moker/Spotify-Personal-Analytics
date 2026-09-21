import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px

ORDEM_DIAS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
              'Friday', 'Saturday', 'Sunday']
NOMES_DIAS = {'Monday': 'Seg', 'Tuesday': 'Ter', 'Wednesday': 'Qua',
              'Thursday': 'Qui', 'Friday': 'Sex', 'Saturday': 'Sáb',
              'Sunday': 'Dom'}
TABELAS_NECESSARIAS = ['streams', 'gold_horas_mensais', 'gold_artista_mes']
FAIXAS_DURACAO = ['Menos de 30 s', '30 s a 2 min', 'Mais de 2 min']


def carregar_dados(caminho_db):
    """Lê a camada silver (view `streams`) e as tabelas gold do spotify.db."""
    if not Path(caminho_db).exists():
        raise FileNotFoundError(caminho_db)

    conn = sqlite3.connect(caminho_db)
    try:
        existentes = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}
        faltando = [t for t in TABELAS_NECESSARIAS if t not in existentes]
        if faltando:
            raise ValueError(
                "O banco não tem as tabelas: " + ", ".join(faltando) +
                ". Gere o banco de novo com `python etl.py \"data/arquivo.zip\"`.")
        return {
            'streams': pd.read_sql("SELECT * FROM streams", conn),
            'mensal': pd.read_sql("SELECT * FROM gold_horas_mensais", conn),
            'artista_mes': pd.read_sql("SELECT * FROM gold_artista_mes", conn),
        }
    finally:
        conn.close()


def _periodo(df):
    return df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)


# ---------- Visão geral ----------

def distribuicao_duracao(df):
    """Percentual de plays x percentual de horas por faixa de duração."""
    faixas = pd.cut(df['ms_played'], bins=[0, 30_000, 120_000, float('inf')],
                    labels=FAIXAS_DURACAO, right=False)
    dados = (df.assign(duracao=faixas)
               .groupby('duracao', observed=True)
               .agg(plays=('ms_played', 'size'), minutos=('min_played', 'sum'))
               .reset_index())
    dados['% dos plays'] = 100 * dados['plays'] / dados['plays'].sum()
    dados['% das horas'] = 100 * dados['minutos'] / dados['minutos'].sum()
    longo = dados.melt(id_vars='duracao',
                       value_vars=['% dos plays', '% das horas'],
                       var_name='metrica', value_name='percentual')
    fig = px.bar(longo, x='duracao', y='percentual', color='metrica',
                 barmode='group', text_auto='.1f',
                 category_orders={'duracao': FAIXAS_DURACAO},
                 labels={'duracao': 'Duração do play',
                         'percentual': 'Percentual', 'metrica': ''},
                 title='Plays curtos: muito volume, pouco tempo')
    return fig


def evolucao_mensal(mensal):
    """Horas por dia em cada mês (corrige o efeito de meses incompletos)."""
    dados = mensal.sort_values(['ano', 'mes']).copy()
    dados['periodo'] = _periodo(dados)
    return px.line(dados, x='periodo', y='horas_por_dia', markers=True,
                   hover_data={'horas': True, 'dias_com_escuta': True},
                   labels={'periodo': 'Mês', 'horas_por_dia': 'Horas por dia',
                           'horas': 'Horas no mês',
                           'dias_com_escuta': 'Dias com escuta'},
                   title='Horas escutadas por dia, mês a mês')


def artista_do_mes(artista_mes):
    """Artista nº 1 de cada mês, com as horas dele naquele mês."""
    dados = artista_mes.sort_values(['ano', 'mes']).copy()
    dados['periodo'] = _periodo(dados)
    return px.bar(dados, x='periodo', y='horas', color='artista',
                  hover_data={'pct_do_mes': ':.1f'},
                  labels={'periodo': 'Mês', 'horas': 'Horas do artista no mês',
                          'artista': 'Artista nº 1',
                          'pct_do_mes': '% das horas do mês'},
                  title='Artista mais ouvido de cada mês')


# ---------- Artistas e faixas ----------

def top_artistas(df, n=15):
    dados = df.groupby('artista')['min_played'].sum().nlargest(n).reset_index()
    dados['horas'] = dados['min_played'] / 60
    return px.bar(dados.sort_values('horas'), x='horas', y='artista',
                  orientation='h',
                  labels={'horas': 'Horas escutadas', 'artista': 'Artista'},
                  title=f'Top {n} artistas (horas)')


def top_faixas(df, n=15):
    dados = (df.groupby(['faixa', 'artista'])['min_played'].sum()
               .nlargest(n).reset_index())
    dados['label'] = dados['faixa'] + ' — ' + dados['artista']
    return px.bar(dados.sort_values('min_played'), x='min_played', y='label',
                  orientation='h',
                  labels={'min_played': 'Minutos escutados', 'label': 'Faixa'},
                  title=f'Top {n} faixas (minutos)')


def skip_rate(df, min_plays=50, n=15):
    stats = df.groupby('artista').agg(plays=('faixa', 'count'),
                                      skip_rate=('pulada', 'mean'))
    stats = (stats[stats['plays'] >= min_plays]
             .sort_values(['skip_rate', 'plays'], ascending=False)
             .head(n).reset_index())
    fig = px.bar(stats.sort_values(['skip_rate', 'plays']),
                 x='skip_rate', y='artista', orientation='h',
                 hover_data=['plays'],
                 labels={'skip_rate': 'Taxa de skip', 'artista': 'Artista',
                         'plays': 'Plays'},
                 title=f'Artistas mais pulados (mín. {min_plays} plays)')
    fig.update_xaxes(tickformat='.0%')
    return fig


# ---------- Hábitos ----------

def por_hora(df):
    dados = df.groupby('hora')['min_played'].sum().reset_index()
    dados['horas'] = dados['min_played'] / 60
    fig = px.bar(dados, x='hora', y='horas',
                 labels={'hora': 'Hora do dia', 'horas': 'Horas escutadas'},
                 title='Em que horas você mais escuta')
    fig.update_xaxes(dtick=1)
    return fig


def por_dia_semana(df):
    dados = (df.groupby('dia_semana')['min_played'].sum()
               .reindex(ORDEM_DIAS).reset_index())
    dados['horas'] = dados['min_played'] / 60
    dados['dia'] = dados['dia_semana'].map(NOMES_DIAS)
    return px.bar(dados, x='dia', y='horas',
                  labels={'dia': 'Dia', 'horas': 'Horas escutadas'},
                  title='Em que dias você mais escuta')
