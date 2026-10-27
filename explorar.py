import pandas as pd
import requests


USUARIO = "edgarrr_45"
url = f"https://api.chess.com/pub/player/{USUARIO}/games/archives"
headers = {"User-Agent": "proyecto-analisis-ajedrez"}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

dict_archives = response.json()
lista_archives = dict_archives["archives"]


partida = requests.get(lista_archives[-1], headers=headers, timeout=30)
partida.raise_for_status()
games = partida.json()
lista_games = games["games"]

def extraer_datos(game, usuario):
    if game["white"]["username"].lower() == usuario.lower():
        color = "blancas"
        mi_lado, lado_rival = "white", "black"
    else:
        color = "negras"
        mi_lado, lado_rival = "black", "white"

    return {
        "url": game["url"],
        "fecha": game["end_time"],
        "mi_color": color,
        "mi_rating": game[mi_lado]["rating"],
        "rating_rival": game[lado_rival]["rating"],
        "mi_resultado": game[mi_lado]["result"],
        "time_class": game.get("time_class"),
        "time_control": game.get("time_control"),
    }

filas = []

for game in lista_games:
    extraido = extraer_datos(game, USUARIO)
    filas.append(extraido)

df = pd.DataFrame(filas)

df["fecha"] = (
    pd.to_datetime(df["fecha"], unit="s")
    .dt.tz_localize("UTC")
    .dt.tz_convert("America/Mexico_City")
)

regla = {
    "win": "victoria",
    "resigned": "derrota",
    "abandoned": "derrota",
    "timeout": "derrota",
    "checkmated": "derrota",
    "repetition": "empate",
    "insufficient": "empate",
    "stalemate": "empate",
}
df["resultado"] = df["mi_resultado"].map(regla)
df["gane"] = df["resultado"] == "victoria"
print(df.groupby("mi_color")["gane"].agg(["mean", "count"]))
print(df["resultado"].isna().sum())
print(df.shape)
print(df.head())
print(df["resultado"].value_counts())
print(df["url"].duplicated().sum())