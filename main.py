import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_ts_segment(index, url, segments_dir):
    """
    Descarga un segmento de video desde una URL proporcionada y lo guarda en un archivo temporal.
    Args:
        index (int): El índice del segmento en el archivo .m3u8 para asegurar el orden correcto.
        url (str): La URL del segmento de video a descargar.
        segments_dir (str): El directorio donde se guardará el archivo temporal del segmento.
    Returns:
        str: La ruta del archivo descargado si tiene éxito, de lo contrario None.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://platzi.com/',
            'Origin': 'https://platzi.com'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        segment_filename = os.path.join(segments_dir, f"segment_{index:05d}.ts")
        with open(segment_filename, "wb") as file:
            file.write(response.content)

        # print(f"Descargado: {segment_filename}")
        return segment_filename
    except Exception as e:
        print(f"Error al descargar {url}: {str(e)}")
        return None

def download_all_segments(m3u8_file, output_dir, file_name, max_workers=5):
    """
    Descarga todos los segmentos de video de un archivo .m3u8 y los combina en un archivo de salida.
    Args:
        m3u8_file (str): La ruta del archivo .m3u8 que contiene las URLs de los segmentos.
        output_dir (str): El directorio donde se guardarán los segmentos y el archivo final.
        max_workers (int): Número máximo de hilos para descargas paralelas.
    """
    segments_dir = os.path.join(output_dir, "segments")
    os.makedirs(segments_dir, exist_ok=True)

    segment_files = []

    with open(m3u8_file, "r") as f:
        urls = [line.strip() for line in f if line.startswith("http")]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(download_ts_segment, index, url, segments_dir): index for index, url in enumerate(urls)
        }

        for future in as_completed(future_to_index):
            result = future.result()
            if result:
                segment_files.append(result)

    # Ordenar los archivos de segmentos antes de combinarlos
    segment_files.sort()

    # Combinar los segmentos descargados en un solo archivo
    combined_file_path = os.path.join(output_dir, f"{file_name}.mp4")
    with open(combined_file_path, "wb") as output_file:
        for segment_file in segment_files:
            with open(segment_file, "rb") as segment:
                output_file.write(segment.read())

    print(f"Descarga completada y archivo combinado: {combined_file_path}")

if __name__ == "__main__":
    m3u8_files = [file for file in os.listdir() if file.endswith(".m3u8")]
    file_name = os.sys.argv[1] if len(os.sys.argv) > 1 else "video"
    output_dir = "output"

    if not m3u8_files:
        print("No se encontraron archivos .m3u8 en el directorio.")
    else:
        m3u8_file = m3u8_files[0]
        print(f"Descargando segmentos desde: {m3u8_file}")
        download_all_segments(m3u8_file, output_dir, file_name)
