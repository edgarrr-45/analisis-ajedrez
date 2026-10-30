import re
import pandas as pd

df = pd.read_csv("partidas.csv")
df["fecha"] = pd.to_datetime(df["fecha"], utc=True).dt.tz_convert("America/Mexico_City")
df = df[(df["rules"] == "chess") & (df["time_class"].isin(["blitz", "rapid", "bullet"]))].copy()


def contar_jugadas(pgn):
    if not isinstance(pgn, str):
        return None
    texto = pgn.split("\n\n")[-1]               # quedarse solo con las jugadas
    texto = re.sub(r"\{[^}]*\}", "", texto)     # borrar los relojes
    numeros = re.findall(r"(\d+)\.", texto)     # encontrar los números de jugada
    if not numeros:
        return 0
    return max(int(n) for n in numeros)


# Pruebas: la primera partida debe dar 49 y la de la URL, 28
print(contar_jugadas(df["pgn"].iloc[0]))
url = "https://www.chess.com/game/live/184687696548"
print(contar_jugadas(df[df["url"] == url]["pgn"].iloc[0]))

df["jugadas"] = df["pgn"].apply(contar_jugadas)
print(df["jugadas"].describe())
print(df.groupby("mi_resultado")["jugadas"].agg(["median", "mean", "count"]))

sub = df[df["mi_resultado"].isin(["abandoned", "timeout"])]
print(sub.groupby("mi_resultado")["jugadas"].describe())
print(sub.groupby(["mi_resultado", "time_class"])["jugadas"].agg(["median", "count"]))

df["hora"] = df["fecha"].dt.hour
df["corte"] = df["mi_resultado"].isin(["abandoned", "timeout"])

df["franja"] = pd.cut(
    df["hora"],
    bins=[-1, 5, 9, 14, 18, 23],
    labels=["madrugada 0-5", "mañana 6-9", "mediodía 10-14", "tarde 15-18", "noche 19-23"],
)

tabla = df.groupby("franja", observed=True).agg(
    partidas=("url", "count"),
    victorias=("gane", "mean"),
    cortes=("corte", "mean"),
)
print(tabla)

df["anio"] = df["fecha"].dt.year
print(df.groupby(["franja", "anio"], observed=True)["corte"].agg(["mean", "count"]))
print(df.groupby(["time_class", "franja"], observed=True)["corte"].agg(["mean", "count"]))

blitz = df[df["time_class"] == "blitz"].copy()
blitz["abandono"] = blitz["mi_resultado"] == "abandoned"
blitz["tiempo"] = blitz["mi_resultado"] == "timeout"

print(blitz.groupby(["anio", "franja"], observed=True)["corte"].agg(["mean", "count"]))
print(blitz.groupby("franja", observed=True)[["abandono", "tiempo"]].mean())