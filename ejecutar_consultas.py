import sqlite3
import pandas as pd

conexion = sqlite3.connect("partidas.db")

with open("consultas.sql", encoding="utf-8") as archivo:
    texto = archivo.read()

# Cada consulta termina en ";", así que se separan por ese símbolo
for consulta in texto.split(";"):
    consulta = consulta.strip()

    # Saltar trozos vacíos o que solo tengan comentarios
    lineas = [l for l in consulta.splitlines() if l.strip() and not l.strip().startswith("--")]
    if not lineas:
        continue

    titulo = consulta.splitlines()[0]   # la primera línea es el comentario con el título
    print(titulo)
    print(pd.read_sql(consulta, conexion))
    print()

conexion.close()