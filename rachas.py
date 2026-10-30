import pandas as pd

df = pd.read_csv("partidas.csv")
df["fecha"] = pd.to_datetime(df["fecha"], utc=True).dt.tz_convert("America/Mexico_City")
df = df[(df["rules"] == "chess") & (df["time_class"].isin(["blitz", "rapid", "bullet"]))].copy()

blitz = df[df["time_class"] == "blitz"].sort_values("fecha").copy()
blitz["gane_anterior"] = blitz["gane"].shift(1)

print(blitz.groupby("gane_anterior")["gane"].agg(["mean", "count"]))

blitz["minutos_desde_anterior"] = blitz["fecha"].diff().dt.total_seconds() / 60
sesion = blitz[blitz["minutos_desde_anterior"] <= 30]

print(len(sesion))
print(sesion.groupby("gane_anterior")["gane"].agg(["mean", "count"]))

blitz["sigue_pronto"] = blitz["minutos_desde_anterior"].shift(-1) <= 30
resto = blitz.iloc[:-1]

print(resto.groupby("resultado")["sigue_pronto"].agg(["mean", "count"]))

print(resto.groupby("mi_resultado")["sigue_pronto"].agg(["mean", "count"]))

def tipo(resultado):
    if resultado == "win":
        return "victoria"
    if resultado in ["abandoned", "timeout"]:
        return "abandono o tiempo"
    if resultado in ["resigned", "checkmated"]:
        return "derrota limpia"
    return "empate"

resto = resto.copy()
resto["tipo"] = resto["mi_resultado"].map(tipo)
print(resto.groupby("tipo")["sigue_pronto"].agg(["mean", "count"]))