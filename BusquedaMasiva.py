import os
import argparse
import threading
import time
import sys
from datetime import datetime
from collections import defaultdict

#-------------------------------------------------------------------------------
# Clase para gestionar el estado de la búsqueda de forma thread-safe
#-------------------------------------------------------------------------------
class EstadoBusqueda:
    def __init__(self):
        self.archivos_procesados = 0
        self.archivos_con_error = 0
        self.busqueda_activa = True
        self.lock = threading.Lock()
    
    def incrementar_procesados(self):
        with self.lock:
            self.archivos_procesados += 1
    
    def incrementar_errores(self):
        with self.lock:
            self.archivos_con_error += 1
    
    def detener(self):
        self.busqueda_activa = False
    
    def obtener_estadisticas(self):
        with self.lock:
            return self.archivos_procesados, self.archivos_con_error

#-------------------------------------------------------------------------------
# Muestra un indicador de progreso animado con estadísticas en tiempo real
#   -> estado : objeto EstadoBusqueda con las estadísticas actuales
#   <- None
#-------------------------------------------------------------------------------
def heartbeat(estado):
    animacion = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    while estado.busqueda_activa:
        procesados, errores = estado.obtener_estadisticas()
        sys.stdout.write(f'\r{animacion[idx]} Procesando... Archivos: {procesados} | Errores: {errores}')
        sys.stdout.flush()
        idx = (idx + 1) % len(animacion)
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 80 + '\r')  # Limpiar línea
    sys.stdout.flush()

#-------------------------------------------------------------------------------
# Lee los valores a buscar desde un archivo de texto
#   -> fichero_valores : ruta al archivo con los patrones (uno por línea)
#   <- list : lista de valores/patrones a buscar
#-------------------------------------------------------------------------------
def leer_valores_desde_fichero(fichero_valores):
    """Lee los valores a buscar desde un archivo"""
    with open(fichero_valores, 'r', encoding='utf-8') as f:
        valores = [line.strip() for line in f if line.strip()]
    print(f"✓ Cargados {len(valores)} patrones de búsqueda")
    return valores

#-------------------------------------------------------------------------------
# Busca los valores en todos los archivos del directorio de forma recursiva
#   -> valores : lista de patrones a buscar
#   -> directorio_base : directorio raíz donde realizar la búsqueda
#   -> estado : objeto EstadoBusqueda para actualizar estadísticas
#   <- dict : diccionario con los resultados encontrados por cada valor
#-------------------------------------------------------------------------------
def buscar_valores_en_archivos(valores, directorio_base, estado):
    """Busca los valores en todos los archivos del directorio"""
    encontrados = defaultdict(list)
    
    for carpeta_raiz, _, archivos in os.walk(directorio_base):
        for archivo in archivos:
            ruta_completa = os.path.join(carpeta_raiz, archivo)
            try:
                with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()
                    for valor in valores:
                        if valor in contenido:
                            # Contar ocurrencias en el archivo
                            ocurrencias = contenido.count(valor)
                            encontrados[valor].append({
                                'archivo': archivo,
                                'ruta': ruta_completa,
                                'ocurrencias': ocurrencias
                            })
                estado.incrementar_procesados()
            except Exception as e:
                estado.incrementar_errores()
    
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
    """Guarda los resultados en un archivo TSV"""
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("Valor;Fichero;Ruta;Ocurrencias\n")
        for valor in valores_originales:
            if valor in encontrados:
                for match in encontrados[valor]:
                    f.write(f"{valor};{match['archivo']};{match['ruta']};{match['ocurrencias']}\n")
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
    """Muestra un resumen detallado de los resultados"""
    print("\n" + "="*70)
    print("                    RESUMEN DE BÚSQUEDA")
    print("="*70)
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Archivos procesados: {archivos_procesados}")
    print(f"   • Archivos con error: {archivos_con_error}")
    print(f"   • Tiempo de ejecución: {tiempo_ejecucion:.2f} segundos")
    
    valores_encontrados = len([v for v in valores if v in encontrados and encontrados[v]])
    valores_no_encontrados = len(valores) - valores_encontrados
    
    print(f"\n🔍 RESULTADOS DE BÚSQUEDA:")
    print(f"   • Patrones buscados: {len(valores)}")
    print(f"   • Patrones encontrados: {valores_encontrados}")
    print(f"   • Patrones no encontrados: {valores_no_encontrados}")
    
    if encontrados:
        print(f"\n📝 DETALLE POR PATRÓN:")
        for valor in sorted(valores):
            if valor in encontrados and encontrados[valor]:
                total_ocurrencias = sum(match['ocurrencias'] for match in encontrados[valor])
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
    parser = argparse.ArgumentParser(
        description="Buscar valores en archivos de un directorio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python BusquedaMasiva.py -f patrones.txt -d C:\\MiDirectorio
  python BusquedaMasiva.py -f patrones.txt -d C:\\MiDirectorio -i
        """
    )
    parser.add_argument('-f', '--file', required=True, 
                       help="Archivo con los valores a buscar (uno por línea)")
    parser.add_argument('-d', '--directory', required=True, 
                       help="Directorio raíz para la búsqueda")
    parser.add_argument('-i', '--include-missing', action='store_true', 
                       help="Incluir valores no encontrados en el resultado")
    
    # Capturar errores de argumentos y mostrar mensaje personalizado
    try:
        args = parser.parse_args()
    except SystemExit:
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
    if not os.path.exists(args.file):
        print(f"❌ Error: El archivo '{args.file}' no existe")
        return
    
    if not os.path.exists(args.directory):
        print(f"❌ Error: El directorio '{args.directory}' no existe")
        return
    
    # Crear directorio de resultados si no existe
    directorio_resultados = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
    if not os.path.exists(directorio_resultados):
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
    valores = leer_valores_desde_fichero(args.file)
    
    # Iniciar heartbeat
    hilo_heartbeat = threading.Thread(target=heartbeat, args=(estado,), daemon=True)
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
    archivos_procesados, archivos_con_error = estado.obtener_estadisticas()
    tiempo_ejecucion = tiempo_fin - tiempo_inicio
    mostrar_resumen(resultados, valores, archivos_procesados, archivos_con_error, tiempo_ejecucion)
    
    print(f"✅ Resultados guardados en '{archivo_salida}'")

#-------------------------------------------------------------------------------
# Ejecuta el metodo principal si se llama directamente al script. Si se importa, no hace nada.
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()