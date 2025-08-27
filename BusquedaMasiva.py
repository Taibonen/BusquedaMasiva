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
        return [line.strip() for line in f if line.strip()]

def buscar_valores_en_archivos(valores, directorio_base):
    encontrados = {valor: [] for valor in valores}

    for carpeta_raiz, _, archivos in os.walk(directorio_base):
        for archivo in archivos:
            ruta_completa = os.path.join(carpeta_raiz, archivo)
            try:
                with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()
                    for valor in valores:
                        if valor in contenido:
                            encontrados[valor].append((archivo, ruta_completa))
            except Exception as e:
                print(f"No se pudo leer el archivo {ruta_completa}: {e}")
    return encontrados

def guardar_resultados(encontrados, archivo_salida, incluir_no_encontrados):
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("Valor;Fichero\n")
        for valor, coincidencias in encontrados.items():
            if coincidencias:
                for archivo, ruta in coincidencias:
                    f.write(f"{valor};{ruta}\n")
            elif incluir_no_encontrados:
                f.write(f"{valor};N/A\n")

# Argumentos de línea de comandos
parser = argparse.ArgumentParser(description="Buscar valores en archivos de un directorio")
parser.add_argument('-f', '--file', required=True, help="Archivo con los valores a buscar")
parser.add_argument('-d', '--directory', required=True, help="Directorio raíz para la búsqueda")
parser.add_argument('-i', '--include-missing', action='store_true', help="Incluir valores no encontrados en el resultado")
args = parser.parse_args()

# Ejecutar
print("-- Iniciamos el proceso de búsqueda --")
valores = leer_valores_desde_fichero(args.file)
resultados = buscar_valores_en_archivos(valores, args.directory)
guardar_resultados(resultados, "resultados.tsv", args.include_missing)

print("---- Búsqueda completada. Resultados guardados en 'resultados.tsv' ------")