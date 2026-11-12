-- 1. Porcentaje de victorias por modo de juego y color
SELECT
    time_class AS modo,
    mi_color AS color,
    COUNT(*) AS partidas,
    ROUND(AVG(gane) * 100, 1) AS pct_victorias
FROM partidas
GROUP BY time_class, mi_color
ORDER BY time_class, mi_color;

-- 1b. Lo mismo, pero solo para blitz
SELECT
    time_class AS modo,
    mi_color AS color,
    COUNT(*) AS partidas,
    ROUND(AVG(gane) * 100, 1) AS pct_victorias
FROM partidas
WHERE time_class = 'blitz'
GROUP BY time_class, mi_color
ORDER BY time_class, mi_color;

-- 2. Victorias y abandonos o tiempos por franja del día
SELECT
    CASE
        WHEN hora <= 5  THEN 'madrugada 0-5'
        WHEN hora <= 9  THEN 'mañana 6-9'
        WHEN hora <= 14 THEN 'mediodía 10-14'
        WHEN hora <= 18 THEN 'tarde 15-18'
        ELSE                 'noche 19-23'
    END AS franja,
    COUNT(*) AS partidas,
    ROUND(AVG(gane) * 100, 1) AS pct_victorias,
    ROUND(AVG(mi_resultado IN ('abandoned', 'timeout')) * 100, 1) AS pct_cortes
FROM partidas
GROUP BY franja
ORDER BY MIN(hora);


-- 3. Rachas en blitz: % de victorias según el resultado de la partida anterior
WITH blitz AS (
    SELECT
        gane,
        LAG(gane) OVER (ORDER BY fecha) AS gane_anterior
    FROM partidas
    WHERE time_class = 'blitz'
)
SELECT
    gane_anterior,
    COUNT(*) AS partidas,
    ROUND(AVG(gane) * 100, 1) AS pct_victorias
FROM blitz
WHERE gane_anterior IS NOT NULL
GROUP BY gane_anterior
ORDER BY gane_anterior;

-- 4. Rating en blitz: promedio móvil de las últimas 30 partidas (las 5 más recientes)
SELECT
    ROW_NUMBER() OVER (ORDER BY fecha) AS n,
    fecha,
    mi_rating,
    ROUND(AVG(mi_rating) OVER (
        ORDER BY fecha
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 1) AS rating_suave
FROM partidas
WHERE time_class = 'blitz'
ORDER BY fecha DESC
LIMIT 5;

-- 2b. Lo mismo que la 2, pero solo para blitz
SELECT
    CASE
        WHEN hora <= 5  THEN 'madrugada 0-5'
        WHEN hora <= 9  THEN 'mañana 6-9'
        WHEN hora <= 14 THEN 'mediodía 10-14'
        WHEN hora <= 18 THEN 'tarde 15-18'
        ELSE                 'noche 19-23'
    END AS franja,
    COUNT(*) AS partidas,
    ROUND(AVG(gane) * 100, 1) AS pct_victorias,
    ROUND(AVG(mi_resultado IN ('abandoned', 'timeout')) * 100, 1) AS pct_cortes
FROM partidas
WHERE time_class = 'blitz'
GROUP BY franja
ORDER BY MIN(hora);

-- 5. Blitz: % que siguió jugando en menos de 30 minutos, según cómo terminó la partida
WITH blitz AS (
    SELECT
        mi_resultado,
        CAST(strftime('%s', LEAD(fecha) OVER (ORDER BY fecha)) AS INTEGER)
            - CAST(strftime('%s', fecha) AS INTEGER) AS segundos_hasta_siguiente
    FROM partidas
    WHERE time_class = 'blitz'
)
SELECT
    CASE
        WHEN mi_resultado = 'win' THEN 'victoria'
        WHEN mi_resultado IN ('abandoned', 'timeout') THEN 'abandono o tiempo'
        WHEN mi_resultado IN ('resigned', 'checkmated') THEN 'derrota limpia'
        ELSE 'empate'
    END AS tipo,
    COUNT(*) AS partidas,
    ROUND(AVG(segundos_hasta_siguiente <= 1800) * 100, 1) AS pct_sigue_pronto
FROM blitz
WHERE segundos_hasta_siguiente IS NOT NULL
GROUP BY tipo
ORDER BY pct_sigue_pronto DESC;