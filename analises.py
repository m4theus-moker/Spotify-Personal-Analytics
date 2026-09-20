import sqlite3
import pandas as pd
import plotly.express as px

ORDEM_DIAS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
              'Friday', 'Saturday', 'Sunday']
NOMES_DIAS = {'Monday': 'Seg', 'Tuesday': 'Ter', 'Wednesday': 'Qua',
              'Thursday': 'Qui', 'Friday': 'Sex', 'Saturday': 'Sáb',
              'Sunday': 'Dom'}


def carregar_dados(caminho_db):
    conn = sqlite3.connect(caminho_db)
    df = pd.read_sql("SELECT * FROM streams", conn)
    conn.close()
    return df


def horas_por_ano(df):
    dados = df.groupby('ano')['min_played'].sum().reset_index()
    dados['horas'] = dados['min_played'] / 60
    return px.bar(dados, x='ano', y='horas',
                  labels={'ano': 'Ano', 'horas': 'Horas escutadas'},
                  title='Horas escutadas por ano')


def top_artistas(df, n=15):
    dados = df.groupby('artista')['min_played'].sum().nlargest(n).reset_index()
    dados['horas'] = dados['min_played'] / 60
    return px.bar(dados.sort_values('horas'), x='horas', y='artista',
                  orientation='h', title=f'Top {n} artistas (horas)')


def top_faixas(df, n=15):
    dados = (df.groupby(['faixa', 'artista'])['min_played'].sum()
               .nlargest(n).reset_index())
    dados['label'] = dados['faixa'] + ' — ' + dados['artista']
    return px.bar(dados.sort_values('min_played'), x='min_played', y='label',
                  orientation='h', title=f'Top {n} faixas (minutos)')


def skip_rate(df, min_plays=50, n=15):
    stats = df.groupby('artista').agg(plays=('faixa', 'count'),
                                      skip_rate=('pulada', 'mean'))
    stats = (stats[stats['plays'] >= min_plays]
             .sort_values(['skip_rate', 'plays'], ascending=False)
             .head(n).reset_index())
    fig = px.bar(stats.sort_values(['skip_rate', 'plays']),
                 x='skip_rate', y='artista', orientation='h',
                 hover_data=['plays'],
                 labels={'skip_rate': 'Taxa de skip', 'artista': 'Artista'},
                 title=f'Artistas mais pulados (mín. {min_plays} plays)')
    fig.update_xaxes(tickformat='.0%')
    return fig

def evolucao_mensal(df):
    d = df.copy()
    d['periodo'] = d['ano'].astype(str) + '-' + d['mes'].astype(str).str.zfill(2)
    mensal = d.groupby('periodo')['min_played'].sum().reset_index()
    mensal['horas'] = mensal['min_played'] / 60
    return px.line(mensal, x='periodo', y='horas', markers=True,
                   labels={'periodo': 'Mês', 'horas': 'Horas escutadas'},
                   title='Horas escutadas por mês')

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