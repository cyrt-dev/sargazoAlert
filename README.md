# Sargazo Alert — HackMaya

Prototipo de **alerta temprana** de sargazo en el Caribe mexicano: entrenamos modelos de machine learning con series históricas para pronosticar biomasa regional a horizontes.

## Qué es este proyecto

Sargazo Alert busca anticipar condiciones de sargazo a partir de datos satelitales e información meteorológica/oceanográfica, para que una app pueda mostrar una señal temprana a residentes, turismo y equipos de respuesta.

| Hoy (MVP de entrenamiento) | Todavía no |
|----------------------------|------------|
| Pronóstico regional de biomasa SATsum (producto 2dr) | Arribazón costera / toneladas en playa |
| Baseline de persistencia + XGBoost por horizonte D+1…D+7 | API pública ni app cliente |
| Artefactos locales (modelos, métricas, gráficos, forecast demo) | Validación de llegada a costa con este archivo solo |

La biomasa del Excel es una **estimación satelital regional**, no toneladas efectivamente arribadas a playas.

## Fuentes de datos

| Fuente | Rol |
|--------|-----|
| **SATsum** (SIMAR / CONABIO, CC BY 4.0) | Serie diaria regional usada **hoy** para entrenar y evaluar el modelo (hoja `Datos` del Excel). |
| **ERA5** (ECMWF / Copernicus) | Fuente prevista para enriquecer el modelo con variables atmosféricas y oceánicas (viento, presión, etc.). **Aún no entra al notebook P0.** |

- Excel actual: `data/raw/SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632.xlsx`
- Objetivo: columna oficial `2-day combined product · 2dr · OFFICIAL daily figure (t)`
- Cobertura aproximada: ~6,165 filas diarias (2010-01-01 → 2026-11-19)

## Instalación

1. Usar **Python 3.11** o **3.12**.
2. Crear el entorno e instalar dependencias:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Confirmar que el Excel SATsum está en:

`data/raw/SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632.xlsx`

4. Abrir y ejecutar de arriba a abajo:

`notebooks/entrenamiento_satsum.ipynb`

5. Revisar salidas en `outputs/{models,metrics,figures,forecasts}/`.

## Cómo funciona (resumen)

1. Carga la serie histórica SATsum desde un único Excel local (sin servicios externos en P0).
2. Construye features causales y un split temporal con purga para evitar filtración (leakage).
3. Evalúa un **baseline de persistencia** y un **XGBoost Regressor** por horizonte D+1…D+7.
4. Exporta modelos (`.joblib`), métricas, figuras y un forecast demostrativo bajo `outputs/`.

## Prueba puntual del forecast demo (smoke test)

Chequeo manual sobre `outputs/forecasts/demo_forecast_d1_d7.csv`
(origen `2026-10-10`, horizontes D+1…D+7 → targets `2026-10-11` … `2026-10-17`).

**No** reemplaza el backtest completo (`outputs/metrics/`, `backtest_predictions_test.csv`).
Efectividad = `100% − error relativo` respecto al valor observado.

### Promedio agregado D+1…D+7

| Métrica | Valor |
|---------|-------|
| Promedio predicho | 5164.34 t |
| Promedio observado (ventana) | 4037.63 t |
| Error absoluto | +1126.71 t (sobreestimación) |
| Error relativo | ≈ 27.9% |
| Efectividad | ≈ 72.1% |

### Horizonte D+1 (fecha objetivo `2026-10-11`)

| Métrica | Valor |
|---------|-------|
| Observado (`y_true`, backtest) | 12880.0 t |
| Predicho | 11292.98 t |
| Error absoluto | −1587.02 t (subestimación) |
| Error relativo | ≈ 12.3% |
| Efectividad | ≈ 87.7% |

En esta emisión, **D+1** quedó más cerca (~12% de error) que el **promedio de los 7 días** (~28% de error). Un solo origen no mide la calidad global del modelo.

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

## Limitaciones

- El producto 2dr toma la observación del día o, si falta, la del día anterior; **no es un promedio de dos días**.
- Cero no siempre equivale a ausencia de sargazo.
- Features y evaluación usan cortes temporales con purga para evitar leakage.
- ERA5, OpenDrift, clasificación/hurdle y etiquetas de playa **no** forman parte del entrenamiento P0 actual.
- Las cifras de la sección “Prueba puntual…” son de **una sola fecha de emisión**; para MAE/RMSE por horizonte usá `outputs/metrics/`.

## Siguiente paso

1. Incorporar **ERA5** (y otros forzamientos) como features en fecha de emisión.
2. **Crear una API** que sirva los pronósticos del modelo entrenado a una app (consulta de horizontes D+1…D+7, estado del modelo y metadatos).
3. Cuando existan etiquetas costeras verificadas, evaluar modelos de llegada/cantidad por playa.

## Checklist P0

- [x] El notebook corre de inicio a fin solo con el Excel local y `requirements.txt`.
- [x] Baseline de persistencia y XGBoost evaluados en D+1…D+7.
- [x] Modelos, métricas y una predicción demostrativa guardados en `outputs/`.
- [x] README deja claro el alcance regional (sin afirmar arribazón costera) y el roadmap API + ERA5.
- [x] Smoke test del demo forecast (origen 2026-10-10) documentado: promedio D+1…D+7 y D+1 vs observado, con % de efectividad.
