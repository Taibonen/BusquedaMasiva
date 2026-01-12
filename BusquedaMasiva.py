import os
import argparse
import threading
import time
import sys
from datetime import datetime
from collections import defaultdict

#-------------------------------------------------------------------------------
# Clase para gestionar el estado de la búsqueda de forma thread-safe
# -> self : instancia de la misma clase
#-------------------------------------------------------------------------------
class EstadoBusqueda:
    def __init__(self):
        self.archivos_procesados = 0 # Archivos que han sido procesados
        self.archivos_con_error = 0  # Archivos que generaron error
        self.busqueda_activa = True # Indica si la búsqueda está en curso
        self.lock = threading.Lock() # Bloqueo para sincronización de hilos
    
    def incrementar_procesados(self): # Incrementa el contador de archivos procesados
        with self.lock:
            self.archivos_procesados += 1
    
    def incrementar_errores(self): # Incrementa el contador de archivos con error
        with self.lock:
            self.archivos_con_error += 1
    
    def detener(self): # Detiene la búsqueda
        self.busqueda_activa = False
    
    def obtener_estadisticas(self): # Devuelve las estadísticas actuales 
        with self.lock:
            return self.archivos_procesados, self.archivos_con_error

#-------------------------------------------------------------------------------
# Muestra un indicador de progreso animado con estadísticas en tiempo real
#   -> estado : objeto EstadoBusqueda con las estadísticas actuales
#   <- None
#-------------------------------------------------------------------------------
def heartbeat(estado):
    animacion = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'] #Lista todos los simbolos Animación de carga
    idx = 0
    while estado.busqueda_activa: # Mientras la búsqueda esté activa
        procesados, errores = estado.obtener_estadisticas()
        sys.stdout.write(f'\r{animacion[idx]} Procesando... Archivos: {procesados} | Errores: {errores}') # Escribe por pantalla la animacion y estadísticas
        sys.stdout.flush() # Asegura que se imprima inmediatamente

        # Avanza al siguiente símbolo de la animación. Si llega al final, vuelve al inicio. 
        # Para ello usa el %, que lo que hace es devolver el resto de la división entre 10 que es el valor de len(animacion).
        # Así, cuando idx sea 10, el resultado será 0 y volverá al inicio.
        idx = (idx + 1) % len(animacion)

        time.sleep(0.1) # Pausa breve para controlar la velocidad de la animación
    sys.stdout.write('\r' + ' ' * 80 + '\r')  # Limpiar línea
    sys.stdout.flush()

#-------------------------------------------------------------------------------
# Lee los valores a buscar desde un archivo de texto
#   -> fichero_valores : ruta al archivo con los patrones (uno por línea)
#   <- list : lista de valores/patrones a buscar
#-------------------------------------------------------------------------------
def leer_valores_desde_fichero(fichero_valores):
    """Lee los valores a buscar desde un archivo""" # Es un docstring que describe la función. Se puede acceder a él con help().
    with open(fichero_valores, 'r', encoding='utf-8') as f: # Abre el archivo en modo lectura con codificación UTF-8
        valores = [line.strip() for line in f if line.strip()] # Lee cada línea, elimina espacios y filtra líneas vacías
    print(f"✓ Cargados {len(valores)} patrones de búsqueda") # Muestra cuántos patrones se han cargado
    return valores

#-------------------------------------------------------------------------------
# Busca los valores en todos los archivos del directorio de forma recursiva
#   -> valores : lista de patrones a buscar
#   -> directorio_base : directorio raíz donde realizar la búsqueda
#   -> estado : objeto EstadoBusqueda para actualizar estadísticas
#   <- dict : diccionario con los resultados encontrados por cada valor
#-------------------------------------------------------------------------------
def buscar_valores_en_archivos(valores, directorio_base, estado):
    """Busca los valores en todos los archivos del directorio""" # Es un docstring que describe la función. Se puede acceder a él con help().
    encontrados = defaultdict(list) # Diccionario para almacenar los resultados encontrados
    
    for carpeta_raiz, _, archivos in os.walk(directorio_base): # Recorre el directorio de forma recursiva
        for archivo in archivos:
            ruta_completa = os.path.join(carpeta_raiz, archivo) # Construye la ruta completa del archivo
            try:
                with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f: # Abre el archivo en modo lectura
                    contenido = f.read() # Lee el contenido del archivo
                # Busca cada valor en el contenido del archivo
                    for valor in valores:
                        if valor in contenido:
                            # Contar ocurrencias en el archivo
                            ocurrencias = contenido.count(valor)
                            encontrados[valor].append({ # Almacena los detalles de la coincidencia en el diccionario encontrados[]
                                'archivo': archivo,
                                'ruta': ruta_completa,
                                'ocurrencias': ocurrencias
                            })
                estado.incrementar_procesados() # Actualiza el contador de archivos procesados
            except Exception as e:
                estado.incrementar_errores() # Actualiza el contador de archivos con error
    
    return dict(encontrados)

#-------------------------------------------------------------------------------
# Guarda los resultados de la búsqueda en un archivo TSV
#   -> encontrados : diccionario con los resultados encontrados
#   -> archivo_salida : ruta del archivo donde guardar los resultados
#   -> incluir_no_encontrados : bool, si se deben incluir valores no encontrados
#   -> valores_originales : lista con todos los valores buscados originalmente
#   <- None
#-------------------------------------------------------------------------------
def guardar_resultados(encontrados, archivo_salida, incluir_no_encontrados, valores_originales):
    """Guarda los resultados en un archivo TSV"""  # Es un docstring que describe la función. Se puede acceder a él con help().
    with open(archivo_salida, 'w', encoding='utf-8') as f: # Abre el archivo en modo escritura con codificación UTF-8
        f.write("Valor;Fichero;Ruta;Ocurrencias\n") # Escribe la cabecera del archivo TSV
        for valor in valores_originales:
            if valor in encontrados:
                for match in encontrados[valor]: # Recorre cada coincidencia encontrada para el valor
                    f.write(f"{valor};{match['archivo']};{match['ruta']};{match['ocurrencias']}\n") # Escribe los detalles de la coincidencia
            elif incluir_no_encontrados:
                f.write(f"{valor};N/A;N/A;0\n")

#-------------------------------------------------------------------------------
# Muestra un resumen detallado de los resultados de la búsqueda
#   -> encontrados : diccionario con los resultados encontrados
#   -> valores : lista de todos los valores buscados
#   -> archivos_procesados : número total de archivos procesados
#   -> archivos_con_error : número de archivos que generaron error
#   -> tiempo_ejecucion : tiempo total en segundos que tomó la búsqueda
#   <- None
#-------------------------------------------------------------------------------
def mostrar_resumen(encontrados, valores, archivos_procesados, archivos_con_error, tiempo_ejecucion):
    """Muestra un resumen detallado de los resultados"""  # Es un docstring que describe la función. Se puede acceder a él con help().
    print("\n" + "="*70)
    print("                    RESUMEN DE BÚSQUEDA")
    print("="*70)
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Archivos procesados: {archivos_procesados}")
    print(f"   • Archivos con error: {archivos_con_error}")
    print(f"   • Tiempo de ejecución: {tiempo_ejecucion:.2f} segundos")
    

    valores_encontrados = len([v for v in valores if v in encontrados and encontrados[v]]) 
    # [v for v in valores if v in encontrados and encontrados[v]] ->  crea una lista de valores que fueron encontrados
    #   -> v for v in valores : itera sobre cada valor en la lista original (valores)
    #   -> if v in encontrados and encontrados[v] : filtra solo aquellos valores que están en el diccionario de encontrados y que tienen al menos una coincidencia 
    #   Finalmente, len(...) cuenta cuántos valores cumplen esa condición. 


    valores_no_encontrados = len(valores) - valores_encontrados    # Calcula el número de valores no encontrados restando los encontrados del total
    
    print(f"\n🔍 RESULTADOS DE BÚSQUEDA:")
    print(f"   • Patrones buscados: {len(valores)}")
    print(f"   • Patrones encontrados: {valores_encontrados}")
    print(f"   • Patrones no encontrados: {valores_no_encontrados}")
    
    if encontrados: # Si se encontraron coincidencias
        print(f"\n📝 DETALLE POR PATRÓN:")
        for valor in sorted(valores): # Recorre los valores en orden alfabético
            if valor in encontrados and encontrados[valor]: 
                total_ocurrencias = sum(match['ocurrencias'] for match in encontrados[valor])
                # match['ocurrencias'] for match in encontrados[valor] -> crea un generador que itera sobre cada coincidencia (match) encontrada para el valor actual (valor) y 
                #                   extrae el número de ocurrencias de esa coincidencia.
                # sum(...) -> suma todos los números de ocurrencias generados por el generador anterior, dando el total de ocurrencias del valor en todos los archivos donde fue encontrado.


                num_archivos = len(encontrados[valor])
                print(f"   • '{valor}':")
                print(f"     - Encontrado en {num_archivos} archivo(s)")
                print(f"     - Total de ocurrencias: {total_ocurrencias}")
            else:
                print(f"   • '{valor}': No encontrado")
    
    print("\n" + "="*70 + "\n")

#-------------------------------------------------------------------------------
# Función principal que coordina la ejecución del script
#   <- None
#-------------------------------------------------------------------------------
def main():
    # Argumentos de línea de comandos
    parser = argparse.ArgumentParser( # Crea el objeto parser para manejar los argumentos de línea de comandos
        description="Buscar valores en archivos de un directorio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python BusquedaMasiva.py -f patrones.txt -d C:\\MiDirectorio
  python BusquedaMasiva.py -f patrones.txt -d C:\\MiDirectorio -i
        """
    )
    parser.add_argument('-f', '--file', required=True, 
                       help="Archivo con los valores a buscar (uno por línea)") # Añade un argumento al parser: Archivo que contiene los patrones a buscar
    parser.add_argument('-d', '--directory', required=True, 
                       help="Directorio raíz para la búsqueda") # Añade un argumento al parser: Directorio donde se realizará la búsqueda
    parser.add_argument('-i', '--include-missing', action='store_true', 
                       help="Incluir valores no encontrados en el resultado") # Añade un argumento al parser:  (Opcional) Incluir patrones no encontrados en el resultado
    
    # Capturar errores de argumentos y mostrar mensaje personalizado
    try:
        args = parser.parse_args() # Parsea los argumentos de línea de comandos y los guarda en la variable "<args>". Para ello primero se han tenido que decalrar con el "parser.add_argument()"
    except SystemExit: # Captura la excepción que se lanza cuando hay un error en los argumentos
        print("\n" + "="*70)
        print("❌ ERROR: Faltan parámetros obligatorios")
        print("="*70)
        print("\n📋 USO CORRECTO DEL SCRIPT:\n")
        print("  python BusquedaMasiva.py -f ARCHIVO_PATRONES -d DIRECTORIO_BUSQUEDA\n")
        print("📝 PARÁMETROS:")
        print("  -f, --file        Archivo con los patrones a buscar (uno por línea)")
        print("  -d, --directory   Directorio donde realizar la búsqueda")
        print("  -i, --include-missing  (Opcional) Incluir patrones no encontrados\n")
        print("💡 EJEMPLOS:")
        print("  python BusquedaMasiva.py -f patrones.txt -d C:\\MisDocumentos")
        print("  python BusquedaMasiva.py -f buscar.txt -d C:\\Proyectos -i")
        print("\n" + "="*70 + "\n")
        return
    
    # Validaciones
    if not os.path.exists(args.file): # Verifica si el archivo de patrones existe
        print(f"❌ Error: El archivo '{args.file}' no existe")
        return
    
    if not os.path.exists(args.directory):  # Verifica si el directorio de búsqueda existe
        print(f"❌ Error: El directorio '{args.directory}' no existe")
        return
    
    # Crear directorio de resultados si no existe
    directorio_resultados = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados") # Directorio donde se guardarán los resultados
    if not os.path.exists(directorio_resultados): # Verifica si el directorio de resultados existe
        os.makedirs(directorio_resultados)
        print(f"✓ Directorio de resultados creado: {directorio_resultados}")
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archivo_salida = os.path.join(directorio_resultados, f"{timestamp}_Resultados.tsv")
    
    # Iniciar
    print("\n" + "="*70)
    print("           BÚSQUEDA MASIVA DE PATRONES EN ARCHIVOS")
    print("="*70)
    print(f"\n📂 Directorio: {args.directory}")
    print(f"📄 Archivo de patrones: {args.file}")
    print(f"💾 Archivo de salida: {archivo_salida}\n")
    
    # Crear objeto de estado y leer valores
    estado = EstadoBusqueda()
    valores = leer_valores_desde_fichero(args.file) # Lee los patrones desde el archivo especificado y los guarda en la variable "valores"
    
    # Iniciar heartbeat
    hilo_heartbeat = threading.Thread(target=heartbeat, args=(estado,), daemon=True) # Crea un hilo para la función heartbeat
    hilo_heartbeat.start()
    
    # Ejecutar búsqueda
    print("\n🔍 Iniciando búsqueda...")
    tiempo_inicio = time.time()
    resultados = buscar_valores_en_archivos(valores, args.directory, estado)
    tiempo_fin = time.time()
    
    # Detener heartbeat
    estado.detener()
    time.sleep(0.2)  # Esperar a que termine la animación
    
    # Guardar resultados
    guardar_resultados(resultados, archivo_salida, args.include_missing, valores)
    
    # Mostrar resumen
    archivos_procesados, archivos_con_error = estado.obtener_estadisticas() # Obtiene las estadísticas finales
    tiempo_ejecucion = tiempo_fin - tiempo_inicio
    mostrar_resumen(resultados, valores, archivos_procesados, archivos_con_error, tiempo_ejecucion)
    
    print(f"✅ Resultados guardados en '{archivo_salida}'")

#-------------------------------------------------------------------------------
# Ejecuta el metodo principal si se llama directamente al script. Si se importa, no hace nada.
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()