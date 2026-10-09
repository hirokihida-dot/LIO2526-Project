# Handoff: Sistema de previsión de ventas (sector automoción)

## Visión general

Dashboard ligero para un proyecto universitario. El usuario carga el histórico de ventas por modelo de vehículo y el sistema:

1. Predice las ventas futuras con un sistema estadístico en tres fases (línea base, Holt-Winters y gradient boosting).
2. Predice las ventas de un modelo nuevo sin histórico mediante una curva de difusión de Bass calibrada con modelos análogos.
3. Simula escenarios de precio, promoción, incentivos y estacionalidad.
4. Exporta los resultados.

**Stack elegido:** Python de principio a fin. Front en **Dash (Plotly)**; modelos en Python (statsmodels, scikit-learn / LightGBM o XGBoost, pandas).

## Sobre los archivos de diseño

Los archivos de `prototipo/` son **referencias de diseño hechas en HTML**: un prototipo interactivo que muestra el aspecto y el comportamiento previstos. **No es código de producción para copiar.** La tarea es **recrear este diseño en Dash** con sus patrones habituales (`dash.html`, `dcc`, callbacks, `dcc.Graph` con Plotly) y sustituir los cálculos simulados del prototipo por los modelos reales en Python.

Abre `prototipo/prevision-ventas-standalone.html` en cualquier navegador. Funciona sin conexión.

## Fidelidad

**Alta fidelidad (hi-fi).** Los colores, la tipografía, el espaciado, los textos y las interacciones son definitivos. Usa el sistema de diseño *Industry* (`design/industry.css`) tal cual.

Los **números** del prototipo son simulados. El cálculo real debe hacerlo el backend Python.

---

## Estructura del proyecto (arquitectura hexagonal)

Regla de dependencias: `presentation → core → ports` y `adapters → core` (implementa puertos, consume dominio). Nunca al revés: el núcleo no importa Dash, Plotly ni Flask, y no conoce los adaptadores.

```
.
├── README.md / CLAUDE.md          # especificación e instrucciones para agentes
├── design/industry.css            # única fuente del sistema de diseño Industry
├── prototipo/                     # referencia visual (no es código de producción)
├── data/ventas_ejemplo.csv        # dataset de ejemplo (5.480 filas)
├── pyproject.toml                 # metadatos, dependencias y configuración de pytest
├── Makefile                       # run / test aislados del entorno ROS
├── tests/
│   ├── core/                      # unitarios de dominio y casos de uso
│   ├── adapters/                  # naive, ets, bass, escenarios, csv_reader, exportador
│   └── e2e/                       # smoke de arranque de la app Dash
└── app/
    ├── app.py                     # entrypoint: Dash(__name__, use_pages=True), layout raíz
    ├── assets/
    │   └── industry.css           # copia de design/industry.css (Dash la sirve sola)
    ├── presentation/              # adaptadores directos (UI)
    │   ├── pages/
    │   │   ├── datos.py           # 01 Carga de datos      → path "/datos"
    │   │   ├── prevision.py       # 02 Previsión           → path "/" (pantalla inicial)
    │   │   ├── modelos.py         # 03 Comparativa modelos → path "/modelos"
    │   │   ├── lanzamiento.py     # 04 Lanzamiento         → path "/lanzamiento"
    │   │   ├── escenarios.py      # 05 Escenarios          → path "/escenarios"
    │   │   └── exportar.py        # 06 Exportar            → path "/exportar"
    │   ├── components/
    │   │   ├── layout.py          # sidebar, cabecera, card blueprint, kpi_card, seg_control
    │   │   └── charts.py          # plantilla Plotly común y banda de IC
    │   └── ui/
    │       └── formatting.py      # formato es-ES: miles «.», decimal «,», « %»
    ├── core/                      # EL HEXÁGONO — sin Dash, Plotly, Flask ni I/O
    │   ├── domain/
    │   │   ├── entities.py        # Dataset, ForecastFrame (periodo, prevision, ic_inf, ic_sup)
    │   │   ├── params.py          # constantes de negocio: segmentos, motorizaciones, campañas…
    │   │   └── metricas.py        # MAPE, RMSE, cobertura del IC
    │   ├── ports/
    │   │   ├── forecaster.py      # Protocol Forecaster (fases intercambiables)
    │   │   ├── dataset_reader.py  # Protocol lectura/validación CSV/Excel
    │   │   └── exporters.py       # Protocol exportación CSV «;» / JSON
    │   └── usecases/
    │       ├── carga_dataset.py   # upload → validar → asignar columnas → agregar
    │       ├── prever.py          # fases + backtest → previsión e IC 95 %
    │       ├── comparar_modelos.py
    │       ├── lanzamiento.py     # Bass con calibración de análogos
    │       ├── escenarios.py      # palancas sobre la previsión base
    │       └── exportar.py
    └── adapters/
        ├── csv_reader.py          # pandas: detección de columnas y separador
        ├── naive_stacional.py     # fase 1
        ├── holt_winters.py        # fase 2 (statsmodels)
        ├── gbm_exogenas.py        # fase 3 (LightGBM) — pendiente de implementar
        ├── bass.py                # difusión de Bass para lanzamientos
        ├── escenario_palancas.py  # precio, promoción, incentivo, estacionalidad
        ├── exportador.py          # DataFrame → CSV «;» / JSON
        └── caching.py             # flask-caching clave (hash_dataset, sku, granularidad)
```

Estado compartido entre páginas: `dcc.Store(id="store-dataset")` (dataset procesado en JSON o la ruta de un parquet en disco) y `dcc.Store(id="store-filtros", storage_type="local")` con `{sku, granularidad, horizonte}`. Todo va en el layout raíz.

---

## Datos

### Formato de entrada (CSV o Excel)

| Columna | Tipo | Obligatoria |
|---|---|---|
| `fecha` | AAAA-MM-DD | Sí |
| `sku` | Texto (modelo) | Sí |
| `unidades` | Entero | Sí |
| `precio` | Decimal (€) | No |
| `promocion` | 0 / 1 | No |

Se aceptan como separador `,` y `;`. Las columnas se detectan por nombre (`fecha|date`, `sku|modelo|producto`, `unid|cant|ventas|units|qty`) y el usuario puede reasignarlas.

### Dataset de ejemplo: `data/ventas_ejemplo.csv`

- 5.480 filas: 5 modelos × 1.096 días (del 1 oct 2023 al 30 sep 2026), frecuencia diaria.
- Es la misma serie simulada que usa el prototipo. Generación: `base × (1 + tendencia·años) × estacionalidad_mes × patrón_día_semana × (1 + 0,2·ruido gaussiano)`.
- Estacionalidad mensual (ene→dic): `.86 .92 1.10 1.00 1.07 1.22 1.14 .68 .90 .97 .98 1.08`.
- Patrón semanal (dom→sáb): `.35 1.08 1.05 1.05 1.08 1.18 1.21`.
- `promocion = 1` en junio y julio de 2025. Es solo una marca para probar la lectura de variables exógenas: el ejemplo **no** incluye el efecto de la promoción en las ventas.

| SKU | Nombre | Segmento | Base/día | Tendencia anual | Precio |
|---|---|---|---|---|---|
| VEL | Vela | Compacto · gasolina | 34 | +2 % | 21.500 € |
| NOR | Nordic | SUV · híbrido | 46 | +9 % | 34.900 € |
| VOL | Volt-E | SUV · eléctrico | 12 | +32 % | 39.900 € |
| ARI | Aria | Berlina · diésel | 21 | −8 % | 31.200 € |
| BRI | Brisa | Comercial · diésel | 16 | +3 % | 27.800 € |

### Agregación

- **Diaria:** sin cambios.
- **Semanal:** semanas de lunes a domingo. Solo cuentan las semanas completas; la semana en curso pasa a ser el primer periodo de previsión.
- **Mensual:** inicio de mes (`MS`).

| Granularidad | Ventana histórica mostrada | Horizontes | Ventana de backtest |
|---|---|---|---|
| Diaria | 90 días | 30 / 60 / 90 días | 30 días |
| Semanal | 52 semanas | 12 / 26 / 52 semanas | 12 semanas |
| Mensual | 24 meses | 6 / 12 / 18 meses | 6 meses |

---

## Modelos (contrato para el backend)

Todas las funciones de previsión devuelven un `DataFrame` con estas columnas: `periodo, prevision, ic_inf, ic_sup` (IC 95 %).

- **Fase 1: naïve estacional.** `ŷ_t = y_{t−m}`, con m = 12 / 52 / 364 según la granularidad. Es la referencia mínima que cualquier modelo debe superar.
- **Fase 2: Holt-Winters (ETS).** `ExponentialSmoothing(trend="add", damped_trend=True, seasonal="mul", seasonal_periods=m)`. El IC sale de simulación o de los residuos.
- **Fase 3: gradient boosting.** Variables: retardos, medias móviles, mes, día de la semana, festivos, `precio`, `promocion` y matriculaciones del sector (opcional). El IC sale de regresión cuantílica (α = 0,025 y 0,975) o de conformal prediction. **Es el modelo activo por defecto** (etiqueta «Modelo activo · Fase 3»).
- **Métricas:** `MAPE = mean(|y−ŷ|/y)`, `RMSE = sqrt(mean((y−ŷ)²))` y cobertura del IC, es decir, el % de observaciones reales dentro del intervalo. La comparativa de modelos usa los últimos 12 meses (mensual) como conjunto de test.
- **Bass (lanzamiento).** `F(t) = (1 − e^{−(p+q)t}) / (1 + (q/p)·e^{−(p+q)t})`; ventas del mes t = `m·(F(t+1) − F(t)) · estacionalidad_mes`, para 24 meses.
  - `m` = base del segmento × factor de motorización × `(precio_ref/precio)^0.9`. Si hay análogos, se mezcla al 50 % con `media(ventas 12 m de los análogos) × 1,7`.
  - Bases por segmento: Compacto 9.500 (precio de referencia 22.000 €), SUV 12.500 (33.000 €), Berlina 6.500 (31.000 €), Comercial 5.200 (28.000 €).
  - Motorización: Gasolina f = 1 y q = 0,30; Híbrido f = 1,08 y q = 0,36; Eléctrico f = 0,72 y q = 0,44.
  - Campaña: p = 0,018 (Baja), 0,03 (Media) o 0,05 (Alta).
  - IC del mes t: `±1,96·(0,09 + 0,007·t)`.
  - Son valores de partida razonables para calibrar con datos reales.
- **Escenarios** (12 meses, mensual, se aplican a cada SKU y después se suman):
  - Estacionalidad: suavizada = `media + (v−media)·0,5`; acentuada = `·1,5`.
  - Precio: `× (1 − 1,4·Δprecio)` (elasticidad −1,4).
  - Promoción, solo en los meses del periodo elegido (Primavera = mar–may, Verano = jun–jul, Fin de año = nov–dic): `× (1 + 1,6·descuento)`.
  - Incentivo público: `× 1,14` en eléctricos y `× 1,03` en el resto.
  - Ingresos = `unidades × precio × (1+Δprecio) × (1−descuento en meses de promo)`.

---

## Pantallas

El layout raíz es un grid de dos columnas: sidebar fija de `232px` y contenido `minmax(0,1fr)`. El contenido lleva padding de `28px 36px 56px` y separación vertical de `28px` entre bloques.

**Sidebar:** fondo `--color-accent-900` (#1d2d3d), sticky y con 100vh de alto.
- Marca: cuadrado de 36px con borde `--color-accent-400` y el texto «SPV». Al lado, «Previsión de ventas» en Barlow Condensed 19/600 blanco y «AUTOMOCIÓN · V0.1» en 10px, mayúsculas, tracking .1em, `--color-accent-400`.
- Navegación: 6 ítems con número `01–06` (10px, `--color-accent-400`), icono Lucide de 18px (stroke 1.5) y etiqueta de 14px.
  - Ítem activo: fondo `rgba(255,255,255,.08)`, texto #fff y barra izquierda de 2px en `--color-accent-400`.
  - Ítem inactivo: texto `--color-neutral-300`.
  - Iconos: upload, chart-line, layers, rocket, sliders-horizontal, download.
- Pie: «DATASET ACTIVO», el nombre del archivo y «5 modelos · 1.096 días».

**Cabecera de página** (común a todas las pantallas):
- Antetítulo en 11px, mayúsculas, tracking .1em, `--color-accent-700` (p. ej. «02 · PREVISIÓN»).
- Título h1 de 42px en Barlow Condensed 600.
- Subtítulo de 15px en `--color-neutral-700`.
- A la derecha, las etiquetas `.tag-neutral` «Datos hasta 30 sep 2026» y `.tag-accent` «Modelo activo · Fase 3».
- Línea inferior de 1px en `--color-divider`.

**Card patrón:** `.card.blueprint` con las cuatro marcas `<i class="corner tl|tr|bl|br">`, padding de 20px, transparente (sin fondo) y sin redondeo. En Dash: `html.Div(className="card blueprint", children=[html.I(className="corner tl"), …])`.

**KPI card:** card blueprint con kicker (10px, mayúsculas, `--color-accent-700`), valor (Barlow Condensed 40/600, line-height 1), unidad (14px neutral-700) y meta (12px neutral-700). Grid `repeat(auto-fit, minmax(210px,1fr))` con gap de 24px.

**Control segmentado:** `.seg` con `.seg-opt`. El activo tiene fondo `--color-accent` y texto `--color-bg`. En Dash puede ser `dcc.RadioItems` con clases o botones con callback.

### 01 · Carga de histórico (`/datos`)
- Subtítulo: «Importa las ventas históricas por modelo de vehículo. El sistema valida el formato y agrega la serie a diaria, semanal o mensual.»
- Fila 1, dos cards:
  - «Dataset activo»: tag «Validado», nombre del archivo y specs Registros / Modelos / Desde / Hasta / Frecuencia.
  - «Formato esperado»: la tabla de la sección Datos.
- Zona de subida: `dcc.Upload` con borde discontinuo de 1px `--color-neutral-500` (`--color-accent` y fondo `--color-accent-100` al arrastrar), icono file-spreadsheet de 36px y los textos «Arrastra aquí un archivo CSV o Excel» / «o haz clic para seleccionarlo · ventas diarias por modelo, máx. 50 MB».
- Botón secundario «Cargar dataset de ejemplo».
- Tras subir un archivo:
  - Card «Vista previa» con las primeras 6 filas, el nº de filas y el tamaño.
  - Card «Asignación de columnas» con 3 desplegables (fecha / SKU / unidades) y un checklist (Correcto / Pendiente).
  - Botón primario blueprint «Validar y procesar», deshabilitado hasta que las 3 columnas estén asignadas.
  - Al procesar, aviso con fondo `--color-accent-100`: «Serie agregada y lista para previsión.» y el botón «Ver previsión →».

### 02 · Previsión (`/`)
- Filtros: «Modelo de vehículo» (Toda la gama + 5 SKU), «Granularidad» (Diaria / Semanal / Mensual) y «Horizonte» (3 opciones según la granularidad).
- 4 KPI:
  - «Ventas últimos 12 meses», con el % frente a los 12 meses anteriores.
  - «Previsión próximos N …», con el % frente a los N periodos anteriores.
  - «MAPE» y «RMSE», ambos con la meta «Backtest · últimos X».
- Gráfico «Histórico y previsión»:
  - Línea real de 2px en `--color-accent-800`.
  - Previsión discontinua (7-5) de 2,2px en `--color-accent`.
  - Banda IC 95 % en `--color-accent-300` con opacidad .6.
  - Zona de previsión sombreada en `--color-accent-100`, con una línea vertical discontinua en el corte y el rótulo «PREVISIÓN →».
  - Tooltip oscuro (`--color-accent-900`) con el periodo, el valor en uds y «Previsión · IC 95 %: a – b» o «Ventas reales».
- Debajo, dos cards:
  - «Detalle por periodo»: tabla con Periodo, Previsión, IC 95 % y vs. año anterior; máximo 12 filas.
  - «Previsión por modelo»: tabla con Modelo, Previsión y Cuota con barra en `--color-accent`. Al pulsar una fila se filtra por ese SKU; al volver a pulsarla se vuelve a toda la gama.

### 03 · Comparativa de modelos (`/modelos`)
- Selector de SKU y el texto «Granularidad mensual · ventana de test: …».
- 3 cards, una por fase: kicker «Fase N · …», muestra del trazo, nombre, descripción, MAPE / RMSE / Cobertura IC y la etiqueta «Menor error» en la de menor MAPE. Al hacer clic se muestra u oculta la serie en el gráfico (opacidad .5 cuando está oculta).
- Trazos:
  - Fase 1: neutral-600 discontinuo «2 4».
  - Fase 2: accent-400 discontinuo «8 4».
  - Fase 3: accent continuo.
  - Ventas reales: accent-900 de 2,4px.

### 04 · Lanzamiento sin histórico (`/lanzamiento`)
- Formulario (columna izquierda): Nombre, Segmento (seg ×4), Motorización (seg ×3), Precio (slider de 15.000 a 60.000 en pasos de 500), Mes de lanzamiento (de nov 2026 a oct 2027), Inversión en campaña (Baja / Media / Alta) y Modelos análogos (chips conmutables).
- Resultados (columna derecha):
  - 3 KPI: Ventas primer año con su IC, Mes de máximas ventas y Total 24 meses (% del mercado potencial).
  - Gráfico de Bass de 24 meses con banda IC.
  - Los parámetros `m · p · q` se muestran a la derecha del título.

### 05 · Escenarios (`/escenarios`)
- Palancas (columna izquierda): SKU, Variación de precio (de −15 a +15 %), Descuento promocional (de 0 a 25 %), Periodo de la promoción, Estacionalidad, interruptor «Incentivo público a la compra» y botón «Restablecer».
- Resultados (columna derecha):
  - 3 KPI: Unidades 12 meses, Ingresos estimados (en M€) y Mayor impacto (mes y Δ uds).
  - Gráfico con la base (neutral-600, discontinua) y el escenario (accent, continuo); los meses con promoción se sombrean en accent-100.
  - Nota con los supuestos de elasticidad.

### 06 · Exportar (`/exportar`)
- Configuración (columna izquierda):
  - Resumen de SKU · granularidad · horizonte y el enlace «Cambiar en Previsión →».
  - Casillas de contenido: Previsión puntual (obligatoria), IC 95 %, Métricas y Escenario.
  - Formato: CSV (separador `;`) o JSON.
  - Botón primario «Descargar {archivo}». En Dash, usar `dcc.Download` con `dcc.send_data_frame`.
- Vista previa (columna derecha): tabla con las primeras 8 filas y las líneas de métricas y escenario si están marcadas.
- Nombre del archivo: `prevision_{sku}_{granularidad}_{horizonte}.{csv|json}`.

**Comportamiento adaptable:** en Lanzamiento, Escenarios y Exportar se usa `flex-wrap`: el formulario con `flex: 1 1 300px` y los resultados con `flex: 3 1 520px`. Así los resultados pasan debajo del formulario cuando la pantalla es estrecha.

---

## Gráficos (plantilla Plotly)

Crea una plantilla Plotly común en `components/charts.py`:

```python
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Barlow, system-ui, sans-serif", size=12, color="#5d5d60"),
    margin=dict(l=54, r=14, t=24, b=30), hovermode="x unified", showlegend=False,
    xaxis=dict(showgrid=False, linecolor="rgba(29,31,32,.16)", ticks=""),
    yaxis=dict(gridcolor="#d4d4d7", zeroline=False, tickformat="~s", nticks=6),
    hoverlabel=dict(bgcolor="#1d2d3d", font_color="#ffffff", bordercolor="#1d2d3d"),
)
```

- La banda IC se dibuja con dos trazas: `ic_sup` y luego `ic_inf` con `fill="tonexty"`, `fillcolor="rgba(181,217,253,.6)"` y `line_width=0`.
- La zona de previsión es un `add_vrect(fillcolor="#eef6ff", line_width=0, layer="below")` y el corte un `add_vline(line_dash="dot")`.
- Las leyendas van en HTML encima del gráfico, como en el prototipo, no dentro de Plotly.
- `config={"displayModeBar": False}`.

## Interacciones y estado

| Estado | Dónde | Disparador |
|---|---|---|
| `sku`, `granularidad`, `horizonte` | `store-filtros` (local) | Desplegables y controles segmentados; clic en una fila de «Previsión por modelo» |
| dataset procesado | `store-dataset` | «Validar y procesar» / «Cargar dataset de ejemplo» |
| visibilidad de las fases | estado de la página `/modelos` | Clic en la card de la fase |
| parámetros de lanzamiento | estado de la página | Controles del formulario (recálculo en vivo) |
| palancas del escenario | estado de la página | Sliders y controles; «Restablecer» vuelve a precio 0, descuento 10 %, Verano, estacionalidad Normal y sin incentivo |
| opciones de exportación | estado de la página | Casillas y formato; la descarga muestra «Descargado {archivo}.» |

- Hover: cada elemento interactivo tiene tinte de hover y estado pulsado de la rampa del acento. El foco de teclado se marca con `outline: 2px solid var(--color-accent); outline-offset: 2px`. Ya viene en `industry.css`.
- Los recálculos pesados (fase 3, backtesting) deberían cachearse con `flask_caching` y una clave `(hash_dataset, sku, granularidad)`.

## Tokens de diseño (Industry)

Todos están en `design/industry.css`. Usa las variables y no valores literales.

- **Fondo** `--color-bg` #f2f2f3 · **Texto** `--color-text` #1d1f20 · **Acento** `--color-accent` #5980a6 · **Divisor** `rgba(29,31,32,.16)`.
- **Rampa del acento:** 100 #eef6ff · 200 #d6ebff · 300 #b5d9fd · 400 #94bce3 · 500 #749dc4 · 600 #597ea3 · 700 #416180 · 800 #2c455d · 900 #1d2d3d.
- **Rampa neutra:** 100 #f5f5f8 · 200 #e7e7ea · 300 #d4d4d7 · 400 #b7b7ba · 500 #98989b · 600 #7a7a7d · 700 #5d5d60 · 800 #424244 · 900 #2b2b2d.
- **Tipografía:** Barlow Condensed 600 para títulos (h1 42 · h2 32 · h3 25 · h4 20) y Barlow 400/500 para el cuerpo (15px, line-height 1.55). Ambas se cargan desde Google Fonts dentro del CSS.
- **Espaciado:** 3.4 · 6.8 · 10.2 · 13.6 · 20.4 · 27.2 px (`--space-1…8`).
- **Sombras:** `--shadow-sm/md/lg`; el tooltip usa `--shadow-md`.
- **Sin redondeo:** cards, botones, inputs y tags son cuadrados. Las cards no tienen fondo. El botón primario es el único objeto sólido.
- **Texto en acento:** usar `--color-accent-700` para texto pequeño (el acento base solo alcanza 3:1).

## Recursos
- Iconos: [Lucide](https://lucide.dev), stroke 1.5. Usar `dash-iconify` (`lucide:upload`, `lucide:chart-line`, `lucide:layers`, `lucide:rocket`, `lucide:sliders-horizontal`, `lucide:download`, `lucide:file-spreadsheet`, `lucide:check`) o SVG inline.
- No hay imágenes ni fotografías.

## Archivos del paquete

- `README.md`: este documento.
- `CLAUDE.md`: instrucciones breves para agentes.
- `prototipo/prevision-ventas-standalone.html`: el prototipo en un solo archivo que funciona sin conexión. **Es la referencia visual principal.**
- `prototipo/Prevision de Ventas.dc.html`, `support.js` e `industry.css`: el código fuente del prototipo. La lógica de simulación está en la clase `Component` (funciones `fcView`, `mdView`, `lnView`, `scView` y `exView`).
- `design/industry.css`: la hoja de estilos para copiar en `app/assets/`. La referencia vivónica es `prototipo/industry.css`; el `design/` es el que evoluciona.
- `data/ventas_ejemplo.csv`: el dataset de ejemplo (5.480 filas).
- `pyproject.toml`, `Makefile`: bootstrap del proyecto (deps, tests, arranque).
- `app/` + `tests/`: esqueleto hexagonal de la aplicación Dash.
