import os
import time
import random
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import HEADERS, OUTPUT_DIR
from utils import sanitize_filename


class RateLimiter:
    """
    Simple thread-safe rate limiter. Ensures a minimum interval between requests
    across threads and supports global penalization when the server rate-limits.
    """
    def __init__(self, requests_per_second: float = 2.0):
        self.lock = threading.Lock()
        self.interval = 1.0 / max(requests_per_second, 1.0)
        self.next_allowed = 0.0

    def wait(self):
        with self.lock:
            now = time.time()
            sleep_time = max(0.0, self.next_allowed - now)
            # Schedule next allowed time spaced by interval
            self.next_allowed = max(self.next_allowed, now) + self.interval
        if sleep_time > 0:
            time.sleep(sleep_time)

    def penalize(self, seconds: float):
        with self.lock:
            self.next_allowed = max(self.next_allowed, time.time() + max(0.0, seconds))


GLOBAL_RATE_LIMITER = RateLimiter(requests_per_second=2.0)
_rate_lock = threading.Lock()
RATE_LIMIT_HITS = 0

def _record_rate_limit_hit():
    global RATE_LIMIT_HITS
    with _rate_lock:
        RATE_LIMIT_HITS += 1


def download_ts_segment(index: int, ts_url: str, segments_dir: str, max_retries: int = 5):
    """
    Downloads a video segment from a URL and saves it in a temporary file.
    Args:
        index (int): Index of the segment in the .m3u8 file to ensure correct order.
        ts_url (str): The URL of the video segment to download.
        segments_dir (str): The directory where the downloaded segments will be saved.
    Returns:
        str: The path to the saved segment file.
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Global pacing to avoid bursts that trigger 429
            GLOBAL_RATE_LIMITER.wait()
            response = requests.get(ts_url, headers=HEADERS, timeout=20)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                try:
                    wait_seconds = int(retry_after) if retry_after else None
                except ValueError:
                    wait_seconds = None
                if wait_seconds is None:
                    wait_seconds = min(30, 1.5 * (2 ** (attempt - 1)))
                # Record hit and penalize globally to slow down other threads too
                _record_rate_limit_hit()
                GLOBAL_RATE_LIMITER.penalize(wait_seconds)
                time.sleep(wait_seconds + random.uniform(0, 0.2))
                continue

            response.raise_for_status()

            segment_filename = os.path.join(segments_dir, f"segment_{index:05d}.ts")
            with open(segment_filename, "wb") as file:
                file.write(response.content)

            return segment_filename
        except requests.RequestException as e:
            if attempt < max_retries:
                wait_seconds = min(30, 1.5 * (2 ** (attempt - 1)))
                time.sleep(wait_seconds + random.uniform(0, 0.2))
                continue
            print(f"Error al descargar {ts_url}: {str(e)}")
            return None


def download_all_segments(ts_urls: list[str], file_name: str, output_dir: str = OUTPUT_DIR, max_workers: int = 3):
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

    failed_indices = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(download_ts_segment, index, url, segments_dir): index for index, url in enumerate(ts_urls)
        }

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            result = future.result()
            if result:
                segment_files.append(result)
            else:
                failed_indices.append(index)

    if failed_indices:
        print(f"↻ Reintentando {len(failed_indices)} segmentos de forma secuencial...")
        for index in failed_indices:
            url = ts_urls[index]
            result = download_ts_segment(index, url, segments_dir)
            if result:
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