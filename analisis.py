import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


df = pd.read_csv("partidas.csv")
df["fecha"] = pd.to_datetime(df["fecha"], utc=True).dt.tz_convert("America/Mexico_City")
df = df[(df["rules"] == "chess") & (df["time_class"].isin(["blitz", "rapid", "bullet"]))].copy()
print(df.shape)

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
plt.show()