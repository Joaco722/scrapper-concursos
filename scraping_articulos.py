from selenium.webdriver.common.by import By
from datetime import datetime
import re
import unicodedata

def normalizar_texto(texto):
    """
    Limpia el texto para hacer comparaciones exactas sin importar
    acentos, mayúsculas, signos de puntuación raros o espacios extra.
    """
    if not texto:
        return ""
    
    # 1. Convertir a minúsculas
    texto = texto.lower()
    
    # 2. Eliminar acentos (reemplaza á por a, ü por u, etc.)
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    
    # 3. Reemplazar caracteres especiales, comillas tipográficas y guiones por espacios
    texto = re.sub(r'[“”"\'\-\.,_–]', ' ', texto)
    
    # 4. Estandarizar la abreviatura de Número (N°, N.º, Nro) a simplemente " n "
    texto = re.sub(r'n\s*[°º]', ' n ', texto)
    
    # 5. Eliminar espacios múltiples dejándolos en un solo espacio
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def obtener_articulos_pagina(driver, escuelas_clave):
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

            # Comprobación flexible iterando sobre el diccionario de palabras clave
            es_coincidencia = False
            for nombre_escuela, palabras_clave in escuelas_clave.items():
                # Verificamos si TODAS las palabras clave están en el título normalizado
                if all(palabra in titulo_norm for palabra in palabras_clave):
                    es_coincidencia = True
                    break

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