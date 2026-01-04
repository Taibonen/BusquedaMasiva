# BusquedaMasiva

Este script permite realizar una búsqueda masiva de palabras o frases dentro de archivos de texto ubicados en un directorio específico. 
Es útil para localizar rápidamente información en grandes volúmenes de archivos.

## 🚀 Características
- Búsqueda de múltiples valores definidos por el usuario
- Recorrido recursivo por subdirectorios
- Contador de ocurrencias por archivo
- Registro de coincidencias en un archivo de salida con timestamp
- Opción para incluir valores no encontrados
- Indicador de progreso profesional con animación y estadísticas en tiempo real
- Resumen detallado de resultados al finalizar
- Organización automática de resultados en directorio dedicado
- Validación de archivos y directorios antes de ejecutar
- Manejo robusto de errores

## 📦 Requisitos
Este script está desarrollado en Python 3 y no requiere librerías externas.

## 🛠️ Uso
Desde la terminal, ejecuta el script con los siguientes argumentos:

```bash
python BusquedaMasiva.py -f patrones.txt -d /ruta/al/directorio
```

### Argumentos:
- `-f`, `--file`: Ruta al archivo que contiene los valores a buscar (uno por línea)
- `-d`, `--directory`: Directorio raíz donde se realizará la búsqueda
- `-i`, `--include-missing`: (Opcional) Incluir en el resultado los valores no encontrados

### Ejemplos:
```bash
# Búsqueda básica
python BusquedaMasiva.py -f patrones.txt -d C:\MisDocumentos

# Incluyendo valores no encontrados
python BusquedaMasiva.py -f patrones.txt -d C:\Proyectos -i

# Ver ayuda completa
python BusquedaMasiva.py -h
```

## 📁 Estructura de salida

Los resultados se guardan automáticamente en el directorio `./resultados/` con el siguiente formato de nombre:

```
./resultados/20260104-183059_Resultados.tsv
```

El archivo TSV contiene las siguientes columnas:

```
Valor;Fichero;Ruta;Ocurrencias
patron1;documento.txt;C:\ruta\completa\documento.txt;3
patron2;archivo.log;C:\ruta\completa\archivo.log;1
patron3;N/A;N/A;0  # Si no se encontró y se usó -i
```

## 📊 Resumen de ejecución

Al finalizar la búsqueda, el script muestra un resumen completo:

```
======================================================================
                    RESUMEN DE BÚSQUEDA
======================================================================

📊 ESTADÍSTICAS GENERALES:
   • Archivos procesados: 1523
   • Archivos con error: 2
   • Tiempo de ejecución: 12.45 segundos

🔍 RESULTADOS DE BÚSQUEDA:
   • Patrones buscados: 10
   • Patrones encontrados: 7
   • Patrones no encontrados: 3

📝 DETALLE POR PATRÓN:
   • 'error_crítico':
     - Encontrado en 5 archivo(s)
     - Total de ocurrencias: 23
   • 'warning':
     - Encontrado en 15 archivo(s)
     - Total de ocurrencias: 87
   ...
```

## 🎯 Indicador de progreso

Durante la ejecución, el script muestra un indicador animado con estadísticas en tiempo real:

```
⠹ Procesando... Archivos: 1523 | Errores: 2
```

## 📝 Formato del archivo de patrones

El archivo de entrada debe contener un patrón por línea:

```
error
warning
usuario123
datos_importantes
```

## 🧑‍💻 Autor
Taibonen