from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime

# Importamos nuestras funciones
from scraping_articulos import obtener_articulos_pagina
from extraccion_nombres import obtener_nombres_del_articulo

def main():
    # Todas las variaciones posibles de los nombres
    titulos = [
            # --- Variaciones Escuela 1 ---
            'Esc. Educ. Técnica N°1 “Brigadier Gral. Pascual Echague” – Concordia',
            'E E Técnica N°1 “Brigadier Gral. Pascual Echague” – Concordia',
            'E. E. Técnica N°1 “Brigadier Gral. Pascual Echague” – Concordia',
            'E.E. Técnica N° 1 “Brigadier Gral. Pascual Echagüe” – Concordia',
            
            # --- Variaciones Escuela 2 ---
            'E.E.T. N° 2 “Independencia” – Anexo de Formación Profesional – Concordia',
            'E. E. T. N° 2 “Independencia” – Anexo de Formación Profesional – Concordia',
            'E.E.T N° 2 “Independencia” – Anexo de Formación Profesional – Concordia',

            # --- escuela 3 ---
            'Escuela de Educación Agrotécnica N° 152 “M. M. Calderón” – Concordia', 
            
            # --- escuela 4 ---
            'Escuela de Educación Agrotécnica N.º 24 “Gral. San Martín” – Concordia'
        ]

    # ==========================================
    # CONFIGURACIÓN DE VISIBILIDAD (DEBUG)
    # ==========================================
    VER_NAVEGADOR = False  # Cambiá a True cuando necesites ver la pantalla

    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    edge_options.add_experimental_option("detach", True)

    if VER_NAVEGADOR:
        # Si estamos debuggeando, evitamos que la ventana se cierre de golpe
        edge_options.add_experimental_option("detach", True)
    else:
        # Si NO queremos ver el navegador, activamos el modo invisible
        edge_options.add_argument("--headless=new") 
        # También silenciamos algunos mensajes molestos que tira Edge en este modo
        edge_options.add_argument("--disable-gpu")

    # Inicializamos dejando que Selenium Manager descargue y conecte el driver correcto
    driver = webdriver.Edge(options=edge_options)

    base_url = "https://cge.entrerios.gov.ar/category/concursos-nivel-secundario/"

    articulos_encontrados = []
    fechas_globales = set()
    pagina = 1

    # ==========================================
    # FASE 1: Recolección de URLs
    # ==========================================
    print("=== FASE 1: Buscando concursos ===")
    while True:
        url = base_url if pagina == 1 else f"{base_url}page/{pagina}/"
        print(f"Procesando página {pagina}...")
        driver.get(url)
        driver.implicitly_wait(5)

        articulos_pagina, fechas_vistas = obtener_articulos_pagina(driver, titulos)

        fechas_globales.update(fechas_vistas)
        articulos_encontrados.extend(articulos_pagina)

        print(f"   -> Días distintos retrocedidos: {len(fechas_globales)}")

        if len(fechas_vistas) == 0:
            print("¡Alerta! No se detectaron fechas en esta página. Abortando paginación.")
            break

        if len(fechas_globales) > 3:
            print("Se alcanzó el límite histórico de 3 días. Deteniendo paginación.")
            break

        try:
            driver.find_element(By.XPATH, "//a[contains(text(),'Siguiente')]")
            pagina += 1
            time.sleep(1)
        except Exception:
            print("No hay más páginas disponibles.")
            break

    fechas_ordenadas = sorted(list(fechas_globales), key=lambda x: datetime.strptime(x, "%d/%m/%Y"), reverse=True)
    ultimas_tres_fechas = fechas_ordenadas[:3]

    articulos_a_procesar = [
        art for art in articulos_encontrados if art['fecha_texto'] in ultimas_tres_fechas
    ]

    # ==========================================
    # FASE 2: Extracción de Detalles
    # ==========================================
    print(f"\n=== FASE 2: Extrayendo datos ===")
    print(f"Se encontraron {len(articulos_a_procesar)} publicaciones para tus escuelas.")
    
    if len(articulos_a_procesar) > 0:
        time.sleep(2)

    resultados_finales = []

    for articulo in articulos_a_procesar:
        print(f"Procesando: {articulo['titulo']} ({articulo['fecha_texto']})")
        try:
            info_nombres = obtener_nombres_del_articulo(driver, articulo['url'])
            articulo['fecha_sorteo'] = info_nombres['fecha_sorteo']
            articulo['materias'] = info_nombres['materias']
            resultados_finales.append(articulo)
        except Exception as e:
            print(f"Error extrayendo datos del artículo, saltando... ({e})")

    driver.quit()

    # ==========================================
    # MOSTRAR RESULTADOS
    # ==========================================
    print("\nRESULTADOS FINALES\n" + "=" * 50)
    
    if not resultados_finales:
        print("No hubo nuevas publicaciones para estas escuelas en los últimos 3 días.")
        
    for articulo in resultados_finales:
        print(f"Título: {articulo['titulo']}")
        print(f"URL: {articulo['url']}")
        print(f"Fecha: {articulo['fecha_texto']}")
        print(f"Fecha Sorteo: {articulo.get('fecha_sorteo', 'No especificada')}")
        print(
            f"Materias: {', '.join(articulo.get('materias', [])) if articulo.get('materias') else 'No se encontraron materias'}"
        )
        print("-" * 50)


if __name__ == "__main__":
    main()