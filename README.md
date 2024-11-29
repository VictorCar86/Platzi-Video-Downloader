# Platzi Video Downloader

Este script en Python descarga y combina segmentos de video en formato `.ts` listados en un archivo `.m3u8`, y los guarda como un archivo `.mp4` final. Los segmentos se descargan en paralelo utilizando `ThreadPoolExecutor` para mejorar la eficiencia.

## Requisitos Previos

Antes de ejecutar el script, asegúrate de tener instalados los siguientes componentes:

- **Python 3.6+**
- **Biblioteca `requests`**

Puedes instalar la biblioteca necesaria ejecutando:

```bash
pip install requests
```

## Estructura de Archivos

```
/project-directory
│
├── main.py                # El script Python
├── index.m3u8             # Archivo .m3u8 con las URLs de los segmentos
└── output/                # Carpeta donde se guardará el video final
    └── segments/          # Carpeta temporal para almacenar los segmentos descargados
```

## Uso

### 1. Archivo `.m3u8`

Coloca el archivo `.m3u8` en el mismo directorio que el script. Este archivo debe contener una lista de URLs de los segmentos `.ts` que deseas descargar.

### 2. Ejecutar el Script

Para ejecutar el script, abre una terminal en el directorio del script y ejecuta:

```bash
python main.py nombre_archivo_salida
```

- `nombre_archivo_salida`: Nombre del archivo final `.mp4` (sin extensión). Si no se especifica, se utilizará el nombre `video.mp4` de manera predeterminada.

### Ejemplo:

```bash
python main.py mi_video
```

Esto descargará y combinará los segmentos en un archivo llamado `mi_video.mp4` dentro de la carpeta `output`.

## Explicación del Código

### Funciones Principales

#### `download_ts_segment(index, url, segments_dir)`

- Descarga un segmento de video desde una URL específica.
- Guarda el archivo en el directorio `segments` con un nombre basado en su índice.
- Retorna la ruta del archivo descargado.

#### `download_all_segments(m3u8_file, output_dir, file_name, max_workers=5)`

- Lee las URLs del archivo `.m3u8` y las descarga en paralelo.
- Combina todos los segmentos descargados en un solo archivo `.mp4` final.

#### `main`

- Busca automáticamente el archivo `.m3u8` en el directorio actual.
- Llama a `download_all_segments` para realizar la descarga y combinación.

## Directorios y Archivos Generados

- **`output/`**: Carpeta que contiene:
  - `segments/`: Archivos de segmentos descargados (`.ts`).
  - Archivo combinado final en formato `.mp4`.

## Notas

- Si deseas mantener los archivos de segmento después de la combinación, elimina la línea que los borra.
- Aumenta el número de `max_workers` si deseas descargar más segmentos en paralelo, pero ten en cuenta las limitaciones de tu conexión a internet.

---