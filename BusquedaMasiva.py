import os
import argparse
import threading
import time

# Función de heartbeat
def heartbeat():
    while True:
        time.sleep(15)
        print("El script sigue en ejecución. Tenga paciencia")

# Leer los valores desde un fichero de texto
def leer_valores_desde_fichero(fichero_valores):
    with open(fichero_valores, 'r', encoding='utf-8') as f:
        valores = [line.strip() for line in f if line.strip()]
    return valores

# Buscar los valores en los archivos del directorio
def buscar_valores_en_archivos(valores, directorio_base, archivo_salida):
    resultados = []

    for carpeta_raiz, _, archivos in os.walk(directorio_base):
        for archivo in archivos:
            ruta_completa = os.path.join(carpeta_raiz, archivo)
            try:
                with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()
                    for valor in valores:
                        if valor in contenido:
                            resultados.append((valor, archivo, ruta_completa))
            except Exception as e:
                print(f"No se pudo leer el archivo {ruta_completa}: {e}")

    """ with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("Valor : Archivo : Ruta\n")
        for valor, archivo, ruta in resultados:
            f.write(f"{valor} : {archivo} : {ruta}\n") """
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("Valor;Ruta\n")
        for valor, archivo, ruta in resultados:
            f.write(f"{valor};{ruta}\n")

# Configurar argumentos de línea de comandos
parser = argparse.ArgumentParser(description="Buscar valores en archivos de un directorio")
parser.add_argument('-f', '--file', required=True, help="Archivo con los valores a buscar")
parser.add_argument('-d', '--directory', required=True, help="Directorio raíz para la búsqueda")
args = parser.parse_args()

# Iniciar el hilo de heartbeat
threading.Thread(target=heartbeat, daemon=True).start()

# Ejecutar el proceso
print("-- Iniciamos el proceso de búsqueda --")
valores_a_buscar = leer_valores_desde_fichero(args.file)
buscar_valores_en_archivos(valores_a_buscar, args.directory, "resultados.tsv")

print("---- Búsqueda completada. Resultados guardados en 'resultados.tsv' ------")