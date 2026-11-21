# TASKS — Descarga y preparación de ERA5

**Proyecto:** Predicción híbrida de sargazo en el Caribe mexicano  
**Horizonte:** 7 días  
**Objetivo:** Integrar variables meteorológicas históricas con la serie diaria SATsum para entrenar y evaluar un prototipo.  
**Alcance:** Descarga, limpieza, agregación y unión de datos. Sin base de datos ni infraestructura de producción.

## 0. Criterios y decisiones

- [ ] Confirmar el rango de fechas disponible en `SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632.xlsx` (mínimo y máximo de fechas válidas).
- [ ] Inspeccionar las columnas y frecuencia real de SATsum, identificando objetivo, fechas y faltantes.
- [ ] Definir la región geográfica a partir de la cobertura de SATsum; **no asumir** que un único promedio de todo el Caribe representa el arribo a cada playa.
- [ ] Para el MVP, utilizar ERA5 **single levels**, resolución nativa aproximada de 0.25° y agregación diaria.
- [ ] Separar explícitamente las variables disponibles al momento de la predicción para evitar fuga de información.

**Entregables:** `data/raw/era5/`, `data/processed/era5_daily.csv`, `data/processed/model_dataset.csv`.

## 1. Acceso a Copernicus CDS

- [ ] Crear cuenta en https://cds.climate.copernicus.eu/.
- [ ] Revisar y aceptar los términos del dataset ERA5 hourly data on single levels.
- [ ] Instalar dependencias en el entorno Python existente: `pip install cdsapi xarray netCDF4 pandas openpyxl numpy`.
- [ ] Configurar credenciales de CDS mediante el mecanismo recomendado por la versión actual de `cdsapi` (habitualmente archivo `~/.cdsapirc` con URL y token personal).
- [ ] No guardar tokens en el repositorio; agregar `.cdsapirc`, `.env` y datos descargados a `.gitignore` cuando corresponda.
- [ ] Ejecutar una descarga pequeña de prueba (un día, una variable y un área reducida).

**Aceptación:** El script se autentica, descarga y abre un archivo válido sin exponer credenciales.

## 2. Variables meteorológicas iniciales

Descargar inicialmente las siguientes variables del conjunto **ERA5 hourly data on single levels**:

| Variable CDS | Nombre interno | Uso |
|---|---|---|
| `10m_u_component_of_wind` | `u10` | Viento zonal; transporte superficial |
| `10m_v_component_of_wind` | `v10` | Viento meridional; transporte superficial |
| `mean_sea_level_pressure` | `msl` | Contexto atmosférico |
| `total_precipitation` | `tp` | Precipitación, candidata secundaria |

- [ ] Priorizar `u10` y `v10` si el tiempo es limitado.
- [ ] Calcular velocidad del viento: `wind_speed = sqrt(u10**2 + v10**2)`.
- [ ] Mantener los componentes vectoriales: la velocidad sola pierde la dirección.
- [ ] Documentar unidades: viento en m/s, presión en Pa, precipitación en m.
- [ ] Evaluar después variables oceánicas (corrientes, oleaje) desde fuentes compatibles; **ERA5 atmosférico no sustituye corrientes oceánicas observadas o pronosticadas**.

## 3. Descarga histórica

- [ ] Crear `scripts/download_era5.py` con parámetros de inicio, fin, área y carpeta destino.
- [ ] Obtener fechas del Excel SATsum y descargar ERA5 para el periodo coincidente; ampliar hacia atrás únicamente si los rezagos del modelo lo requieren.
- [ ] Configurar área en formato CDS `[norte, oeste, sur, este]` con coordenadas validadas para la zona de estudio.
- [ ] Descargar por mes o por año según el tamaño; preferir lotes mensuales para poder reintentar.
- [ ] Solicitar horas `00:00` a `23:00` cuando se requiera agregación diaria.
- [ ] Guardar archivos originales NetCDF sin modificarlos, con nombres reproducibles como `era5_YYYY_MM.nc`.
- [ ] Implementar reintentos controlados, detección de archivos existentes y registro simple de fallos.
- [ ] Verificar tamaño, variables, cobertura temporal y coordenadas de cada archivo.

**Aceptación:** No faltan días en el periodo seleccionado, salvo indisponibilidad documentada; cada archivo abre con `xarray`.

## 4. Preparación de datos

- [ ] Crear `scripts/process_era5.py`.
- [ ] Normalizar tiempo a UTC y acordar una única convención diaria con SATsum.
- [ ] Resolver dimensiones de `valid_time`/`time`, latitud, longitud y posibles dimensiones extra de los NetCDF.
- [ ] Agregar viento por día (medias de `u10` y `v10`; opcionalmente máximos de velocidad).
- [ ] Para precipitación, revisar la semántica de acumulación del producto antes de calcular totales diarios: **no sumar ciegamente valores acumulados por hora**.
- [ ] Convertir presión a hPa (`msl / 100`) y precipitación a mm (`tp * 1000`) después de la agregación correcta.
- [ ] Crear resumen espacial inicial para la región de estudio; si se dispone de subregiones costeras, mantener resúmenes separados.
- [ ] Exportar `data/processed/era5_daily.csv` con una fila por fecha y región.

**Aceptación:** Sin fechas duplicadas, unidades consistentes y métricas plausibles.

## 5. Unión con SATsum y características

- [ ] Crear `scripts/merge_satsum_era5.py`.
- [ ] Leer el Excel SATsum con `pandas.read_excel` y validar nombre de hoja, fecha y columnas objetivo.
- [ ] Unir por fecha y, cuando aplique, por región; registrar porcentaje de cobertura.
- [ ] Crear rezagos meteorológicos (por ejemplo 1, 3 y 7 días) y ventanas móviles calculadas **solo con datos pasados**.
- [ ] Definir `target_t_plus_7` y, si se evalúan los siete días por separado, objetivos `t+1` a `t+7`.
- [ ] Evitar interpolar objetivos SATsum sin justificación; registrar los faltantes.
- [ ] Exportar `data/processed/model_dataset.csv` y un resumen de columnas y unidades.

**Aceptación:** Dataset sin fuga temporal y con fechas alineadas correctamente.

## 6. Pruebas mínimas

- [ ] **Descarga:** prueba de un día, una variable y región pequeña.
- [ ] **Integridad:** NetCDF legible; variables y coordenadas esperadas.
- [ ] **Tiempo:** sin duplicados; continuidad diaria; zona horaria coherente.
- [ ] **Física:** velocidad de viento no negativa; valores meteorológicos razonables.
- [ ] **Precipitación:** comprobar la agregación con algunos días manualmente.
- [ ] **Unión:** comparar fechas antes y después del `merge`; medir pérdidas.
- [ ] **Fuga de información:** verificar que ninguna característica en fecha `t` usa observaciones posteriores a `t`.
- [ ] **Reproducibilidad:** volver a ejecutar scripts sin descargar ni duplicar datos innecesariamente.

## 7. Orden de ejecución para el prototipo

1. **P0:** Inspeccionar SATsum y determinar fechas/área.
2. **P0:** Activar CDS y descargar muestra ERA5 con `u10`/`v10`.
3. **P0:** Descargar histórico coincidente con SATsum.
4. **P0:** Generar agregados diarios y unirlos con SATsum.
5. **P0:** Entrenar un modelo base y evaluar mediante división temporal.
6. **P1:** Agregar presión, precipitación y rezagos adicionales si mejoran el resultado.
7. **P1:** Evaluar variables oceánicas y pronósticos meteorológicos para operación real a 7 días.

## 8. Estructura mínima de archivos

```text
proyecto-sargazo/
├── data/
│   ├── raw/
│   │   ├── satsum/SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632.xlsx
│   │   └── era5/era5_YYYY_MM.nc
│   └── processed/
│       ├── era5_daily.csv
│       └── model_dataset.csv
├── scripts/
│   ├── download_era5.py
│   ├── process_era5.py
│   └── merge_satsum_era5.py
├── notebooks/
│   └── train_baseline.ipynb
└── TASKS_ERA5.md
```

## 9. Limitaciones importantes

- ERA5 es **reanálisis histórico**, no pronóstico futuro. Para inferencia operativa a 7 días se requerirán pronósticos de viento y otras variables (por ejemplo de ECMWF u otra fuente), o un diseño explícito basado solo en observaciones disponibles hasta la fecha de emisión.
- El viento es un predictor indirecto del desplazamiento de sargazo; no garantiza la llegada a una costa concreta.
- La disponibilidad de ERA5 puede tener retraso respecto a tiempo real. No asumir que el último día ya está publicado.
- Evaluar el modelo mediante partición cronológica y, preferiblemente, backtesting con origen móvil; nunca usar una división aleatoria de días.

**Documentación oficial:**
- https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
- https://cds.climate.copernicus.eu/how-to-api
- https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
