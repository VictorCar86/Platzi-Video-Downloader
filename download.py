import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import HEADERS, OUTPUT_DIR
from utils import sanitize_filename


def download_ts_segment(index: int, ts_url: str, segments_dir: str):
    """
    Downloads a video segment from a URL and saves it in a temporary file.
    Args:
        index (int): Index of the segment in the .m3u8 file to ensure correct order.
        ts_url (str): The URL of the video segment to download.
        segments_dir (str): The directory where the downloaded segments will be saved.
    Returns:
        str: The path to the saved segment file.
    """
    try:
        response = requests.get(ts_url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        segment_filename = os.path.join(segments_dir, f"segment_{index:05d}.ts")
        with open(segment_filename, "wb") as file:
            file.write(response.content)

        return segment_filename
    except Exception as e:
        print(f"Error al descargar {ts_url}: {str(e)}")
        return None


def download_all_segments(ts_urls: list[str], file_name: str, output_dir: str = OUTPUT_DIR, max_workers=5):
    """
    Downloads all video segments listed in a list of URLs in parallel and combines them into a single .mp4 file.
    Args:
        ts_urls (list[str]): URLs list of video segments to download.
        file_name (str): File name without extension.
        output_dir (str, optional): The directory where the downloaded segments will be saved. Defaults to OUTPUT_DIR.
        max_workers (int, optional): The maximum number of threads to use for downloading segments in parallel. Defaults to 5.
    """
    segments_dir = os.path.join(output_dir, "segments")
    os.makedirs(segments_dir, exist_ok=True)

    segment_files = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(download_ts_segment, index, url, segments_dir): index for index, url in enumerate(ts_urls)
        }

        for future in as_completed(future_to_index):
            if result := future.result():
                segment_files.append(result)

    # Sort the segment files before combining
    segment_files.sort()

    # Combine the downloaded segments into a single .mp4 file
    safe_name = sanitize_filename(file_name)
    combined_file_path = os.path.join(output_dir, f"{safe_name}.mp4")
    with open(combined_file_path, "wb") as output_file:
        for segment_file in segment_files:
            with open(segment_file, "rb") as segment:
                output_file.write(segment.read())

    # Delete the temporary segment files
    for segment_file in segment_files:
        os.remove(segment_file)


def download_by_m3u8(file_name: str):
    """
    Download all video segments listed in a .m3u8 file found in the current directory.
    Args:
        file_name (str): File name without extension. If not provided, it will be asked to the user.
    """
    if not file_name:
        file_name = input("Ingrese el nombre del video: ")
    file_name = sanitize_filename(file_name)

    if m3u8_files := [file for file in os.listdir() if file.endswith(".m3u8")]:
        m3u8_file = m3u8_files[0]
        with open(m3u8_file, "r") as f:
            ts_urls = [line.strip() for line in f if line.startswith("https")]
        print("🔗 Descargando segmentos desde:", m3u8_file)
        download_all_segments(ts_urls, file_name)
        print("✅ Descarga de video completada:", f"{sanitize_filename(file_name)}.mp4")
    else:
        print("No se encontraron archivos .m3u8 en el directorio.")