"""ETL em camadas (arquitetura medalhão) do histórico do Spotify.

Uso:
    python etl.py caminho/do/arquivo.zip     (o .zip do Extended Streaming History)
    python etl.py data/raw                   (ou uma pasta que já tenha os JSONs)

Gera o banco data/spotify.db com:
    bronze_streams          dado bruto, como veio nos JSONs (sem as colunas de IP)
    silver_streams          dado limpo e padronizado (fuso, colunas, flags)
    gold_resumo_artistas    horas, plays e skip rate por artista
    gold_horas_mensais      horas por mês e por dia com escuta
    gold_artista_mes        artista nº 1 de cada mês
    streams (view)          atalho para silver_streams (o dashboard usa esse nome)
"""

import argparse
import json
import sqlite3
import zipfile
from contextlib import closing
from fnmatch import fnmatch
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/spotify.db")
RAW_DIR = Path("data/raw")
FUSO = "America/Sao_Paulo"
PLAY_VALIDO_MS = 30_000  # critério do Spotify para contar um stream
PADRAO_ARQUIVO = "Streaming_History_Audio_*.json"

COLUNAS_SILVER = {
    "ts": "ts",
    "master_metadata_track_name": "faixa",
    "master_metadata_album_artist_name": "artista",
    "master_metadata_album_album_name": "album",
    "ms_played": "ms_played",
    "reason_end": "reason_end",
    "skipped": "skipped",
    "shuffle": "shuffle",
}

SQL_GOLD = """
CREATE TABLE gold_resumo_artistas AS
SELECT artista,
       ROUND(SUM(min_played) / 60, 1) AS horas,
       COUNT(*) AS plays,
       SUM(play_valido) AS plays_validos,
       ROUND(AVG(pulada), 4) AS skip_rate
FROM silver_streams
GROUP BY artista;

CREATE TABLE gold_horas_mensais AS
SELECT ano, mes,
       ROUND(SUM(min_played) / 60, 1) AS horas,
       COUNT(DISTINCT SUBSTR(ts, 1, 10)) AS dias_com_escuta,
       ROUND(SUM(min_played) / 60.0 / COUNT(DISTINCT SUBSTR(ts, 1, 10)), 2) AS horas_por_dia
FROM silver_streams
GROUP BY ano, mes;

CREATE TABLE gold_artista_mes AS
WITH por_artista AS (
    SELECT ano, mes, artista, SUM(min_played) / 60 AS horas
    FROM silver_streams
    GROUP BY ano, mes, artista
),
com_ranking AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY ano, mes ORDER BY horas DESC) AS pos,
           SUM(horas) OVER (PARTITION BY ano, mes) AS horas_mes
    FROM por_artista
)
SELECT ano, mes, artista,
       ROUND(horas, 1) AS horas,
       ROUND(100.0 * horas / horas_mes, 1) AS pct_do_mes
FROM com_ranking
WHERE pos = 1;

CREATE VIEW streams AS SELECT * FROM silver_streams;
"""


def localizar_jsons(origem):
    """Aceita um .zip (extrai em data/raw) ou uma pasta com os JSONs.

    Do .zip, extrai só os arquivos de histórico de áudio: o resto do export
    (pagamentos, identidade, mensagens...) não é necessário e nem sai do zip.
    """
    origem = Path(origem)
    if origem.suffix.lower() == ".zip":
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(origem) as z:
            for nome in z.namelist():
                if fnmatch(Path(nome).name, PADRAO_ARQUIVO):
                    z.extract(nome, RAW_DIR)
        origem = RAW_DIR
    arquivos = sorted(origem.rglob(PADRAO_ARQUIVO))
    if not arquivos:
        raise SystemExit(
            f"Nenhum {PADRAO_ARQUIVO} encontrado em {origem}.\n"
            "Confira se o .zip é o 'Extended Streaming History' "
            "(e não o 'Account Data', que tem só StreamingHistory_music_*.json)."
        )
    return arquivos


def construir_bronze(arquivos):
    """Bronze: tudo como veio, exceto o IP (não é necessário e é dado pessoal)."""
    dfs = []
    for arquivo in arquivos:
        with open(arquivo, encoding="utf-8") as f:
            dfs.append(pd.DataFrame(json.load(f)))
    df = pd.concat(dfs, ignore_index=True)
    colunas_ip = [c for c in df.columns if c.startswith("ip_")]
    return df.drop(columns=colunas_ip)


def construir_silver(bronze):
    """Silver: limpo, com fuso local e colunas auxiliares."""
    df = bronze[list(COLUNAS_SILVER)].rename(columns=COLUNAS_SILVER)
    df = df.dropna(subset=["faixa"]).copy()  # remove podcasts e registros sem faixa

    ts = pd.to_datetime(df["ts"], utc=True).dt.tz_convert(FUSO)
    df["ts"] = ts.astype(str)
    df["min_played"] = df["ms_played"] / 60000
    df["ano"] = ts.dt.year
    df["mes"] = ts.dt.month
    df["dia_semana"] = ts.dt.day_name()
    df["hora"] = ts.dt.hour

    df["pulada"] = ((df["skipped"] == True) | (df["reason_end"] == "fwdbtn")).astype(int)  # noqa: E712
    df["ouvida_ate_o_fim"] = (df["reason_end"] == "trackdone").astype(int)
    df["play_valido"] = (df["ms_played"] >= PLAY_VALIDO_MS).astype(int)
    df["skipped"] = (df["skipped"] == True).astype(int)  # noqa: E712
    df["shuffle"] = (df["shuffle"] == True).astype(int)  # noqa: E712

    ordem = ["ts", "faixa", "artista", "album", "min_played", "ms_played", "reason_end",
             "skipped", "shuffle", "ano", "mes", "dia_semana", "hora",
             "pulada", "ouvida_ate_o_fim", "play_valido"]
    return df[ordem]


def limpar_banco(conn):
    """Apaga tabelas e views antigas para reconstruir tudo do zero."""
    objetos = conn.execute(
        "SELECT type, name FROM sqlite_master "
        "WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    for tipo, nome in objetos:
        conn.execute(f'DROP {tipo.upper()} IF EXISTS "{nome}"')
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="ETL medalhão do histórico do Spotify")
    parser.add_argument("origem", help="arquivo .zip do Spotify ou pasta com os JSONs")
    args = parser.parse_args()

    arquivos = localizar_jsons(args.origem)
    print(f"{len(arquivos)} arquivos JSON encontrados")

    bronze = construir_bronze(arquivos)
    silver = construir_silver(bronze)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as conn:
        limpar_banco(conn)
        bronze.to_sql("bronze_streams", conn, index=False)
        silver.to_sql("silver_streams", conn, index=False)
        conn.executescript(SQL_GOLD)

        for tabela in ["bronze_streams", "silver_streams", "gold_resumo_artistas",
                       "gold_horas_mensais", "gold_artista_mes"]:
            n = conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
            print(f"{tabela:<22} {n:>8} linhas")

    print(f"Banco gerado em {DB_PATH}")


if __name__ == "__main__":
    main()
