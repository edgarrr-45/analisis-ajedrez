import time

import pandas as pd
import requests

USUARIO = "edgarrr_45"
HEADERS = {"User-Agent": "proyecto-analisis-ajedrez"}

# None = todos los meses. Para probar, pon un número (por ejemplo 3).
ULTIMOS_MESES = None

REGLA = {
    "win": "victoria",
    "resigned": "derrota",
    "abandoned": "derrota",
    "timeout": "derrota",
    "checkmated": "derrota",
    "repetition": "empate",
    "insufficient": "empate",
    "stalemate": "empate",
    "agreed": "empate",
    "50move": "empate",
    "timevsinsufficient": "empate",
}


def obtener_meses(usuario, headers):
    url = f"https://api.chess.com/pub/player/{usuario}/games/archives"
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()["archives"]


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
        "rules": game.get("rules"),
        "rated": game.get("rated"),
        "pgn": game.get("pgn"),
    }


def descargar_mes(url_mes, headers, usuario):
    response = requests.get(url_mes, headers=headers, timeout=30)
    response.raise_for_status()
    lista_games = response.json()["games"]

    filas = [extraer_datos(game, usuario) for game in lista_games]
    return pd.DataFrame(filas)


def main():
    lista_archives = obtener_meses(USUARIO, HEADERS)
    if ULTIMOS_MESES is None:
        meses = lista_archives
    else:
        meses = lista_archives[-ULTIMOS_MESES:]

    tablas = []
    for url_mes in meses:
        tabla = descargar_mes(url_mes, HEADERS, USUARIO)
        tablas.append(tabla)
        print(f"{url_mes[-7:]}: {len(tabla)} partidas")
        time.sleep(0.5)

    df = pd.concat(tablas, ignore_index=True)

    df["fecha"] = (
        pd.to_datetime(df["fecha"], unit="s")
        .dt.tz_localize("UTC")
        .dt.tz_convert("America/Mexico_City")
    )
    df["resultado"] = df["mi_resultado"].map(REGLA)
    df["gane"] = df["resultado"] == "victoria"

    print(df.shape)
    print("duplicados:", df["url"].duplicated().sum())
    print("sin clasificar:", df["resultado"].isna().sum())
    if df["resultado"].isna().any():
        print(df[df["resultado"].isna()]["mi_resultado"].unique())

    print(df["resultado"].value_counts())
    print(df.groupby("mi_color")["gane"].agg(["mean", "count"]))

    df.to_csv("partidas.csv", index=False)
    print(df["time_class"].value_counts())
    print(df["rules"].value_counts())
    print(df["rated"].value_counts())


if __name__ == "__main__":
    main()
