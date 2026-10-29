import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


df = pd.read_csv("partidas.csv")
df["fecha"] = pd.to_datetime(df["fecha"], utc=True).dt.tz_convert("America/Mexico_City")
df = df[(df["rules"] == "chess") & (df["time_class"].isin(["blitz", "rapid", "bullet"]))].copy()
print(df.shape)

# ---------------------------------------------------------------
# 1. Victorias por modo de juego y color
# ---------------------------------------------------------------
print(df.groupby(["time_class", "mi_color"])["gane"].agg(["mean", "count"]))

tasas = df.groupby(["time_class", "mi_color"])["gane"].mean().unstack()

ax = tasas.plot(kind="bar", figsize=(10, 6))
ax.axhline(0.5, color="gray", linestyle="--")
ax.set_title("Porcentaje de victorias por modo de juego y color")
ax.set_xlabel("Modo de juego")
ax.set_ylabel("Porcentaje de victorias")
ax.set_ylim(0, 0.65)
ax.legend(title="Mi color", loc="upper right")
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
for c in ax.containers:
    ax.bar_label(c, labels=[f"{v:.1%}" for v in c.datavalues])
plt.xticks(rotation=0)
plt.savefig("victorias_por_modo.png", dpi=150, bbox_inches="tight")
plt.close()


# ---------------------------------------------------------------
# 2. Rating en el tiempo, por modo
#    eje="fecha" -> el eje horizontal es la fecha
#    eje="n"     -> el eje horizontal es el número de partida (sin pausas)
# ---------------------------------------------------------------
def graficar_rating(df, modo, ventana=30, eje="fecha"):

    df_modo = df[df["time_class"] == modo].copy()
    df_modo = df_modo.sort_values("fecha")
    df_modo["n"] = range(1, len(df_modo) + 1)  # NUEVO: número de partida
    df_modo["rating_suave"] = df_modo["mi_rating"].rolling(ventana).mean()

    if eje == "fecha":
        titulo = f"Rating en {modo} a lo largo del tiempo"
        etiqueta_x = "Fecha"
        archivo = f"rating_{modo}.png"
    else:
        titulo = f"Rating en {modo} por número de partida"
        etiqueta_x = "Número de partida"
        archivo = f"rating_{modo}_por_partida.png"

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_modo[eje], df_modo["mi_rating"], alpha=0.3, label="Cada partida")
    ax.plot(df_modo[eje], df_modo["rating_suave"], linewidth=2, label=f"Promedio de {ventana} partidas")
    ax.set_title(titulo)
    ax.set_xlabel(etiqueta_x)
    ax.set_ylabel("Rating")
    ax.legend()
    plt.savefig(archivo, dpi=150, bbox_inches="tight")
    plt.close()


ventanas = {"blitz": 30, "rapid": 30, "bullet": 15}

for modo, ventana in ventanas.items():
    graficar_rating(df, modo, ventana)            # por fecha
    graficar_rating(df, modo, ventana, eje="n")   # por número de partida


# ---------------------------------------------------------------
# 3. Partidas por mes
# ---------------------------------------------------------------
df["mes"] = df["fecha"].dt.strftime("%Y-%m")
partidas_por_mes = df.groupby("mes").size()

print(partidas_por_mes)
print(partidas_por_mes.sum())

fig, ax = plt.subplots(figsize=(12, 5))
partidas_por_mes.plot(kind="bar", ax=ax)
ax.set_title("Partidas por mes")
ax.set_xlabel("Mes")
ax.set_ylabel("Partidas")
plt.xticks(rotation=90, fontsize=8)
plt.savefig("partidas_por_mes.png", dpi=150, bbox_inches="tight")
plt.close()


# ---------------------------------------------------------------
# 4. Partidas por mes y modo de juego
# ---------------------------------------------------------------
por_mes_modo = df.groupby(["mes", "time_class"]).size().unstack(fill_value=0)

print(por_mes_modo)
print(por_mes_modo.sum())

fig, ax = plt.subplots(figsize=(12, 5))
por_mes_modo.plot(kind="bar", stacked=True, ax=ax)
ax.set_title("Partidas por mes y modo de juego")
ax.set_xlabel("Mes")
ax.set_ylabel("Partidas")
ax.legend(title="Modo")
plt.xticks(rotation=90, fontsize=8)
plt.savefig("partidas_por_mes_modo.png", dpi=150, bbox_inches="tight")
plt.close()