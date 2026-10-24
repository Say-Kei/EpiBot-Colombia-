# EpiBot Colombia · página web (MVP)

Página para celular con el recorrido de 5 pasos: Mi zona → resultado → revisión de fiebre → práctica → plan de la semana. Incluye además las fichas de dengue, chikungunya y malaria y el mapa de Colombia.

## Carpetas

```
epibot-web/
├── index.html            Inicio: consulta de tu zona y las enfermedades
├── zona.html             El recorrido: resultado → revisión → práctica → plan (zona.html?zona=cordoba)
├── enfermedades.html     Fichas con pestañas (enfermedades.html?p=malaria)
├── mapa.html             Mapa del país y lista de departamentos
├── prevencion.html       Acciones de prevención y qué hacer si hay fiebre
├── como-funciona.html    Cómo funciona EpiBot y por qué importa
└── static/
    ├── css/epibot.css         Un solo sistema de diseño para todas las páginas
    ├── js/datos.js            Datos de ejemplo, fichas, práctica y plan semanal
    ├── js/ilustraciones.js    Dibujos SVG
    ├── js/mapa.js             Mapa de Colombia
    ├── js/app.js              Secciones y páginas (cada HTML dice cuál es con data-pagina)
    └── data/                  Aquí va colombia.geojson
```

Todas las páginas comparten el menú, el pie y los mismos 4 scripts. Cada una tiene `<body data-pagina="...">` y `app.js` dibuja lo que le corresponde.

## Cómo probarla

Lo más fácil: doble clic en `index.html`. Se abre en el navegador.

Si quieren probar también la ubicación, ábranla con un servidor desde la carpeta `epibot-web`:

```
python -m http.server 8000
```

Luego abran `http://localhost:8000` y `http://localhost:8000/?zona=cordoba`. Usen F12 → vista de celular.

## Cómo unirla al proyecto Flask

- Si `index.html` se sirve como plantilla, muévanlo a `templates/index.html`. Las rutas `/static/...` ya funcionan con la carpeta `static` por defecto de Flask.
- Copien `static/css` y `static/js` dentro de la carpeta `static` del proyecto.

## Qué falta conectar

1. **API de alertas.** En `app.js`, la función `cargarAlertas()` ya llama a `/api/alertas?departamento=...&desde=...`. Hay que convertir la respuesta al formato de `ZONAS` (en `datos.js`). Mientras no responda, la página usa los datos de ejemplo.
2. **Mi zona con el GeoJSON.** En `app.js`, `miZona()` hoy busca la capital más cercana. Cámbienlo por la búsqueda de punto en polígono con `static/data/colombia.geojson`.
3. **Mapa.** `mapa.js` intenta cargar `/static/data/colombia.geojson`. Si no está, dibuja un contorno aproximado del país.
4. **Páginas enlazadas.** Los botones apuntan a `panel.html`, `fuentes.html` y `centros.html`, que vienen de la rama frone.
5. **Contenido médico.** La persona 4 debe revisar `FICHAS` y `PRACTICA_*` en `datos.js` contra MinSalud, INS y OPS.

## Privacidad

No hay cuentas ni base de datos de usuarios. La ubicación se usa solo en el celular. El progreso del plan se guarda en el propio navegador (`localStorage`) y no sube a ningún servidor.
