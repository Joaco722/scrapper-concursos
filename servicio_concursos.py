"""Servicio reutilizable para consultar concursos del CGE."""

from datetime import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

from extraccion_nombres import obtener_nombres_del_articulo
from scraping_articulos import obtener_articulos_pagina


ESCUELAS_CLAVE = {
    "Técnica 1 Pascual Echagüe": ("tecnica", " n 1 ", "echague"),
    "Técnica 2 Independencia": ("tecnica", " n 2 ", "independencia"),
    "Agrotécnica 152 Calderón": ("agrotecnica", "152", "calderon"),
    "Agrotécnica 24 San Martín": ("agrotecnica", "24", "san martin"),
}

BASE_URL = "https://cge.entrerios.gov.ar/category/concursos-nivel-secundario/"
DIAS_A_CONSULTAR = 3


def crear_driver(ver_navegador=False):
    """Crear un navegador Edge apto para una búsqueda del scraper."""
    opciones = Options()
    opciones.add_argument("--start-maximized")
    opciones.add_experimental_option("excludeSwitches", ["enable-logging"])

    if ver_navegador:
        opciones.add_experimental_option("detach", True)
    else:
        opciones.add_argument("--headless=new")
        opciones.add_argument("--disable-gpu")

    return webdriver.Edge(options=opciones)


def identificar_escuela(titulo):
    """Devolver la escuela que coincide con un título, si existe."""
    from scraping_articulos import normalizar_texto

    titulo_normalizado = normalizar_texto(titulo)
    for escuela, palabras in ESCUELAS_CLAVE.items():
        if all(palabra in titulo_normalizado for palabra in palabras):
            return escuela
    return None


def buscar_concursos(ver_navegador=False):
    """Consultar el CGE y devolver los concursos de los últimos tres días."""
    driver = crear_driver(ver_navegador)
    articulos_encontrados = []
    fechas_globales = set()
    pagina = 1

    try:
        while True:
            url = BASE_URL if pagina == 1 else f"{BASE_URL}page/{pagina}/"
            driver.get(url)
            driver.implicitly_wait(5)

            articulos_pagina, fechas_vistas = obtener_articulos_pagina(
                driver, ESCUELAS_CLAVE
            )
            articulos_encontrados.extend(articulos_pagina)
            fechas_globales.update(fechas_vistas)

            if not fechas_vistas or len(fechas_globales) > DIAS_A_CONSULTAR:
                break

            try:
                driver.find_element(By.XPATH, "//a[contains(text(),'Siguiente')]")
                pagina += 1
                time.sleep(1)
            except Exception:
                break

        fechas_ordenadas = sorted(
            fechas_globales,
            key=lambda fecha: datetime.strptime(fecha, "%d/%m/%Y"),
            reverse=True,
        )
        fechas_recientes = set(fechas_ordenadas[:DIAS_A_CONSULTAR])
        articulos_a_procesar = [
            articulo
            for articulo in articulos_encontrados
            if articulo["fecha_texto"] in fechas_recientes
        ]

        resultados = []
        for articulo in articulos_a_procesar:
            try:
                detalles = obtener_nombres_del_articulo(driver, articulo["url"])
                resultados.append(
                    {
                        **articulo,
                        "escuela": identificar_escuela(articulo["titulo"]),
                        "fecha_sorteo": detalles["fecha_sorteo"],
                        "materias": detalles["materias"],
                    }
                )
            except Exception:
                continue

        return resultados
    finally:
        driver.quit()
