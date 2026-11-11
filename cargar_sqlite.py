import sqlite3
import pandas as pd


df = pd.read_csv("partidas.csv")
df["fecha"] = pd.to_datetime(df["fecha"], utc=True).dt.tz_convert("America/Mexico_City")
df = df[(df["rules"] == "chess") & (df["time_class"].isin(["blitz", "rapid", "bullet"]))].copy()


df["mes"] = df["fecha"].dt.strftime("%Y-%m")
df["hora"] = df["fecha"].dt.hour
df["fecha"] = df["fecha"].dt.strftime("%Y-%m-%d %H:%M:%S")


columnas = [
    "url", "fecha", "mes", "hora", "mi_color", "mi_rating", "rating_rival",
    "mi_resultado", "time_class", "time_control", "resultado", "gane",
]

conexion = sqlite3.connect("partidas.db")
df[columnas].to_sql("partidas", conexion, if_exists="replace", index=False)

print(pd.read_sql("SELECT COUNT(*) AS total FROM partidas", conexion))
print(pd.read_sql("SELECT time_class, COUNT(*) AS partidas FROM partidas GROUP BY time_class", conexion))

conexion.close()