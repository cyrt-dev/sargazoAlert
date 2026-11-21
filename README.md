# SARGASSUM MVP — entrenamiento local

Prototipo experimental para entrenar y evaluar un modelo de **pronóstico regional** de biomasa SATsum a horizontes D+1…D+7 a partir de un único Excel. **Solo requiere Python local y el archivo Excel; no usa servicios externos.**

## Camino rápido

1. Usar Python **3.11** o **3.12**.
2. Crear entorno e instalar dependencias:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Confirmar que el Excel está en:

`data/raw/SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632.xlsx`

4. Abrir y ejecutar de arriba a abajo:

`notebooks/entrenamiento_satsum.ipynb`

5. Revisar salidas en `outputs/{models,metrics,figures,forecasts}/`.

## Qué predice (y qué no)

| Sí | No |
|----|----|
| Serie satelital regional (producto oficial 2dr, ZEE Caribe mexicano) | Arribazón costera / toneladas en playa |
| Comparación temporal vs baseline de persistencia | Validación de llegada a costa con este archivo solo |
| Artefactos locales (`.joblib`, métricas, gráficos) | API, dashboard u OpenDrift en esta etapa |

La biomasa del Excel es una **estimación satelital regional**, no toneladas efectivamente arribadas a playas. **La arribazón costera real no puede validarse con este archivo aislado.**

## Estructura

```text
data/raw/          # Excel SATsum original (inmutable)
data/processed/    # copias procesadas opcionales (Parquet/CSV)
notebooks/         # notebook de entrenamiento P0
outputs/models/    # modelos .joblib
outputs/metrics/   # métricas .csv / .json
outputs/figures/   # gráficos .png
outputs/forecasts/ # predicciones de ejemplo
requirements.txt
README.md
```

## Datos y atribución

- Fuente: SATsum / SIMAR / CONABIO (licencia CC BY 4.0; cita en la hoja `Metadatos` del Excel).
- Hoja de datos: `Datos` (~6,165 filas diarias, 2010-01-01 a 2026-11-19).
- Objetivo: columna oficial `2-day combined product · 2dr · OFFICIAL daily figure (t)`.

## Limitaciones de interpretación

- El producto 2dr toma la observación del día o, si falta, la del día anterior; **no es un promedio de dos días**.
- Cero no siempre equivale a ausencia de sargazo.
- Features y evaluación usan cortes temporales con purga para evitar filtración (leakage).
- ERA5, Copernicus, OpenDrift, clasificación/hurdle y etiquetas de playa quedan fuera del P0.

## Checklist de aceptación (P0)

- [ ] El notebook corre de inicio a fin solo con el Excel local y `requirements.txt`.
- [ ] Baseline de persistencia y XGBoost Regressor evaluados en D+1…D+7.
- [ ] Modelos, métricas y una predicción demostrativa guardados en `outputs/`.
- [ ] README y notebook dejan claro el alcance regional (sin afirmar arribazón costera).

## Siguiente paso

Cuando existan etiquetas costeras verificadas y forzamientos disponibles en fecha de emisión, evaluar modelos de llegada/cantidad por playa. Hasta entonces, este MVP se limita a la serie regional SATsum.
