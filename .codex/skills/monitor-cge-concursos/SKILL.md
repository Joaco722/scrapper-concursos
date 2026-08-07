---
name: monitor-cge-concursos
description: Ejecutar y presentar el monitoreo de concursos docentes del CGE de Entre Ríos. Usar al consultar novedades, interpretar la salida del scraper o preparar resultados para una interfaz gráfica.
---

# Monitorear concursos CGE

## Flujo

1. Revisar `main.py` para confirmar las escuelas configuradas y el límite actual de tres días.
2. Ejecutar `main.py` desde la raíz del proyecto.
3. Informar cada resultado con título, fecha de publicación, fecha de sorteo, materias y enlace.
4. Si no hay resultados, comunicar que no se encontraron publicaciones para las escuelas configuradas en los últimos tres días.

## Criterios

- Conservar los datos obtenidos por el scraper; no inferir una fecha de sorteo o una materia ausente.
- Tratar una excepción de un artículo como un fallo aislado y conservar los demás resultados.
- Usar la función existente de extracción para cualquier futura interfaz, en lugar de duplicar la lógica de Selenium.
