
# BusquedaMasiva

Este script permite realizar una búsqueda masiva de palabras o frases dentro de archivos de texto ubicados en un directorio específico. 
Es útil para localizar rápidamente información en grandes volúmenes de archivos.

## 🚀 Características
- Búsqueda de múltiples valores definidos por el usuario.
- Recorrido recursivo por subdirectorios.
- Registro de coincidencias en un archivo de salida.
- Opción para incluir valores no encontrados.
- Indicador de actividad (heartbeat) para procesos largos.

## 📦 Requisitos
Este script está desarrollado en Python 3 y no requiere librerías externas.

## 🛠️ Uso
Desde la terminal, ejecuta el script con los siguientes argumentos:

```bash
python BusquedaMasiva.py -f valores.txt -d /ruta/al/directorio -i
```

### Argumentos:
- `-f`, `--file`: Ruta al archivo que contiene los valores a buscar (uno por línea).
- `-d`, `--directory`: Directorio raíz donde se realizará la búsqueda.
- `-i`, `--include-missing`: (Opcional) Incluir en el resultado los valores no encontrados.

## 📁 Salida
Se genera un archivo `resultados.tsv` con el siguiente formato:

```
Valor;Fichero
valor1;/ruta/al/archivo1.txt
valor2;/ruta/al/archivo2.txt
valorX;N/A  # Si no se encontró y se usó -i
```

## 🧑‍💻 Autor
Taibonen

