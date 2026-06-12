from selenium.webdriver.common.by import By
from datetime import datetime

def normalizar_texto(texto):
    """Unifica comillas, guiones y espacios para evitar fallos por errores de tipeo en la web."""
    texto = texto.lower()
    texto = texto.replace('“', '"').replace('”', '"').replace("'", '"')
    texto = texto.replace('–', '-').replace('—', '-')
    # Elimina automáticamente los dobles espacios
    return ' '.join(texto.split())

def obtener_articulos_pagina(driver, titulos_buscar):
    """
    Extrae los artículos de la página actual y recolecta todas las fechas vistas
    para llevar un control general del tiempo.
    """
    resultados = []
    fechas_vistas = set()

    contenedores_articulos = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div/div')
    
    # Respaldo de seguridad por si cambia el diseño de la página
    if not contenedores_articulos:
        contenedores_articulos = driver.find_elements(By.XPATH, '//div[h3/a]')

    # Normalizamos los títulos de las escuelas que buscamos
    titulos_buscar_norm = [normalizar_texto(t) for t in titulos_buscar]

    for contenedor in contenedores_articulos:
        try:
            # Extraemos la fecha de CUALQUIER artículo para saber en qué día estamos
            fecha_texto = contenedor.find_element(By.XPATH, './/p').text.strip()
            fechas_vistas.add(fecha_texto)

            # Extraemos título
            enlace = contenedor.find_element(By.XPATH, './/h3/a')
            titulo = enlace.get_attribute('title')
            
            if not titulo:
                titulo = enlace.text.strip()
            else:
                titulo = titulo.strip()
            
            # Normalizamos el título extraído de la web
            titulo_norm = normalizar_texto(titulo)

            # Comprobación flexible
            es_coincidencia = any(t in titulo_norm or titulo_norm in t for t in titulos_buscar_norm)

            if es_coincidencia:
                fecha_obj = datetime.strptime(fecha_texto, "%d/%m/%Y")
                resultados.append({
                    'titulo': titulo,
                    'url': enlace.get_attribute('href'),
                    'fecha_texto': fecha_texto,
                    'fecha_obj': fecha_obj
                })
        except Exception:
            continue

    return resultados, fechas_vistas