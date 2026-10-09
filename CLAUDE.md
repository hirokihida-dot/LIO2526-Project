# CLAUDE.md: Sistema de previsión de ventas

- Lee primero `README.md`: es la especificación completa de pantallas, modelos, tokens y estado.
- Stack: Python, con **Dash (Plotly)** para el front y pandas, statsmodels y LightGBM/XGBoost para los modelos. No introducir frameworks JS.
- La referencia visual es `prototipo/prevision-ventas-standalone.html` (ábrela en el navegador). No copies su código; recrea el diseño en Dash.
- Estilos: solo `design/industry.css` (origen) y su copia `app/assets/industry.css` con sus variables `var(--color-*)`. Usa las clases `.card.blueprint` (con las 4 marcas `corner`), `.btn`, `.seg`, `.table` y `.tag`. Nada redondeado y sin colores nuevos.
- La interfaz está en español, con formato numérico es-ES: separador de miles «.», decimal «,» y « %» con espacio.
- Las funciones de previsión devuelven un DataFrame `periodo, prevision, ic_inf, ic_sup` (IC 95 %). Las métricas son MAPE, RMSE y cobertura del IC.
- Datos de prueba: `data/ventas_ejemplo.csv`.
