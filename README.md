# Scraper CGE — Concursos educativos

Herramienta en Python que consulta las publicaciones de concursos de nivel secundario del Consejo General de Educación de Entre Ríos (CGE). Filtra las escuelas configuradas, revisa las publicaciones de los tres días más recientes y obtiene, cuando están disponibles, la fecha del sorteo y las materias.

## Qué hace

- Navega automáticamente la sección institucional de concursos.
- Busca publicaciones que coincidan con las escuelas configuradas.
- Recorre las páginas necesarias hasta cubrir los últimos tres días con publicaciones.
- Extrae el título, enlace, fecha de publicación, fecha de sorteo y materias.
- Muestra el resultado en la terminal.

## Requisitos

- Python 3.10 o posterior.
- Microsoft Edge instalado.
- Conexión a internet.

## Instalación

Desde la carpeta del proyecto, crea y activa un entorno virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Luego instala las dependencias:

```powershell
pip install -r requirements.txt
```

Selenium administra automáticamente el controlador compatible con Edge en la primera ejecución.

## Uso

Ejecuta el programa desde la carpeta del proyecto:

```powershell
python main.py
```

Por defecto, Edge se ejecuta sin mostrar una ventana. Para ver el navegador durante una prueba, cambia `VER_NAVEGADOR` a `True` en `main.py`.

## Escuelas monitoreadas

La configuración compartida está en `servicio_concursos.py`, en el diccionario `ESCUELAS_CLAVE`. Cada entrada tiene un nombre identificador y las palabras que deben aparecer en el título de una publicación:

```python
"Tecnica 1 Pascual Echague": ("tecnica", " n 1 ", "echague")
```

Para agregar una escuela, incorpora una nueva entrada con palabras clave distintivas. El texto se normaliza antes de compararse: no distingue mayúsculas, acentos, guiones ni espacios repetidos.

## Estructura del proyecto

```text
main.py                    # Orquesta la búsqueda y muestra los resultados
servicio_concursos.py       # Lógica reutilizable de búsqueda para terminal y GUI
app.py                      # Interfaz gráfica local con Streamlit
scraping_articulos.py      # Encuentra publicaciones y aplica el filtro por escuela
extraccion_nombres.py      # Extrae fecha de sorteo y materias de cada publicación
requirements.txt           # Dependencias de Python
.codex/skills/             # Habilidades reutilizables de mantenimiento
```

## Habilidades del proyecto

Las habilidades son guías reutilizables para trabajar de forma consistente sobre el proyecto. Están incluidas dentro de `.codex/skills/`:

- `monitor-cge-concursos`: ejecutar el monitoreo y presentar las novedades.
- `configurar-escuelas-cge`: agregar, quitar o ajustar criterios de escuelas seguidas.
- `mantener-extraccion-cge`: diagnosticar y corregir fallas cuando cambie el sitio del CGE.

## Trabajo futuro

- Permitir administrar las escuelas seguidas desde la interfaz, sin editar código.
- Guardar el historial de búsquedas para distinguir publicaciones nuevas de las ya vistas.
- Incorporar filtros por escuela, fecha y materia.
- Mostrar avisos de error más específicos cuando el sitio del CGE cambie su estructura.
- Evaluar notificaciones automáticas cuando aparezcan novedades relevantes.

## Interfaz gráfica

Con el entorno virtual activo, inicia la aplicación local:

```powershell
streamlit run app.py
```

Se abrirá una página en el navegador donde podrás iniciar la consulta y ver sus resultados.
