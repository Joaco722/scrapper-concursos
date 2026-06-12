import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def es_fecha_sorteo(texto):
    """
    Determina si el texto tiene un patrón que podría corresponder a una fecha de sorteo.
    Verifica que contenga al menos un dígito y la palabra 'de' (en minúsculas o con acentos).
    """
    return bool(re.search(r'\d', texto)) and re.search(r'\bde\b', texto.lower())

def es_hora_sorteo(texto):
    """
    Determina si el texto corresponde a una hora, como '17:30 Hs.' o '14 :00 HORAS'.
    """
    return bool(re.search(r'\b\d{1,2}\s*:\s*\d{2}\s*(?:Hs?\.?|HORAS)?\b', texto, re.IGNORECASE))

def deduplicar(lista):
    """
    Elimina duplicados en la lista preservando el orden.
    """
    visto = set()
    return [x for x in lista if not (x in visto or visto.add(x))]

def obtener_nombres_del_articulo(driver, url, timeout=10):
    """
    Navega al artículo y extrae fecha de sorteo y materias, mejorando la detección de horas
    y considerando elementos <span> dentro de <b> para materias.
    """
    driver.get(url)

    try:
        contenedor = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div[3]/div[2]"))
        )
    except Exception:
        print(f"Tiempo de espera excedido o contenedor no encontrado en: {url}")
        return {'fecha_sorteo': None, 'materias': []}

    driver.execute_script("arguments[0].scrollIntoView();", contenedor)
    WebDriverWait(driver, 3).until(lambda d: True)
    
    # Extraer textos de elementos <strong>
    strong_elements = contenedor.find_elements(By.TAG_NAME, "strong")
    strong_texts = [elem.text.strip() for elem in strong_elements if elem.text.strip()]
    
    fecha_sorteo = None
    materias = []
    i = 0
    while i < len(strong_texts):
        texto = strong_texts[i]
        if fecha_sorteo is None:
            if es_fecha_sorteo(texto):
                fecha_sorteo = texto
                # Verificar si los siguientes elementos son horas
                i += 1
                while i < len(strong_texts):
                    next_text = strong_texts[i]
                    if es_hora_sorteo(next_text):
                        fecha_sorteo += f" {next_text}"
                        i += 1
                    else:
                        break
            else:
                materias.append(texto)
                i += 1
        else:
            materias.append(texto)
            i += 1
    
    # Buscar materias en <span> dentro de <b> si no hay suficientes
    span_elements = contenedor.find_elements(By.XPATH, ".//b/span")
    span_texts = [elem.text.strip() for elem in span_elements if elem.text.strip()]
    for texto in span_texts:
        if texto not in materias:
            materias.append(texto)
    
    materias = deduplicar(materias)
    
    return {'fecha_sorteo': fecha_sorteo, 'materias': materias}