import time, os, pickle, brotli, gzip
from io import BytesIO
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from constants import ROOT_URL, ROOT_DIR, OUTPUT_DIR, EMAIL, PASSWORD
from download import download_all_segments
from utils import sanitize_filename


def save_cookies(driver):
    with open("cookies.pkl", "wb") as archivo:
        pickle.dump(driver.get_cookies(), archivo)

def load_cookies(driver):
    with open("cookies.pkl", "rb") as archivo:
        cookies = pickle.load(archivo)
        for cookie in cookies:
            driver.add_cookie(cookie)

def get_ts_urls(driver: webdriver, downloaded_m3u8_urls: list[str]):
    """
    Extracts the URLs of the .ts segments from the response body of a request to a .m3u8 file.
    Args:
        driver (webdriver): The webdriver instance.
        downloaded_m3u8_urls (list[str]): A list of .m3u8 URLs that have already been downloaded.
    Returns:
        tuple: A tuple containing the URL of the .m3u8 file and a list of URLs of the .ts segments.
    """
    for request in driver.requests:
        if ".m3u8?" in request.url and request.url not in downloaded_m3u8_urls:
            # print("🌐 request URL:", request.url)
            if body := request.response.body:
                try:
                    decoded_body = brotli.decompress(body).decode('utf-8')
                except brotli.error as e:
                    # print("Brotli decompression failed:", e)
                    try:
                        with gzip.GzipFile(fileobj=BytesIO(body), mode='rb') as f:
                            decoded_body = f.read().decode('utf-8')
                    except Exception as e:
                        print("Gzip decompression failed:", e)
                        continue
                body_lines = decoded_body.splitlines()
                urls = [url for url in body_lines if url.startswith("https")]
                return request.url, urls
    return None, []

def get_driver(headless=True):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    # Rely on Selenium Manager to resolve and download the correct ChromeDriver
    return webdriver.Chrome(options=options)

def login_platzi():
    driver = get_driver(headless=False)
    driver.get(f"{ROOT_URL}/login")

    # Simulate manual login
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[id=email]"))
    ).send_keys(EMAIL)

    WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[id=password]"))
    ).send_keys(PASSWORD)

    # Wait until home page is loaded
    WebDriverWait(driver, 90).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".styles-module_Menu__Avatar__FTuh-"))
    )

    save_cookies(driver)
    driver.quit()

def download_course(url):
    driver = get_driver(headless=False)
    driver.get(ROOT_URL)

    load_cookies(driver)
    driver.refresh()  # Refresh to update cookies
    driver.get(url)

    # Wait until title course is loaded
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
    course_title = driver.find_element(By.TAG_NAME, "h1").text
    course_title = sanitize_filename(course_title)

    course_urls = driver.find_elements(By.CSS_SELECTOR, "a[href^='/cursos/']")
    course_urls = [link.get_attribute("href") for link in course_urls if "#" not in link.get_attribute("href")]

    course_dir = os.path.join(OUTPUT_DIR, course_title)
    os.makedirs(course_dir, exist_ok=True)

    print("Descargando curso:", course_title)

    downloaded_m3u8_urls = []

    # Download each class
    for index, course_url in enumerate(course_urls):
        driver.requests.clear()
        driver.get(course_url)

        # Wait for the video to load
        try:
            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.TAG_NAME, "video"))
            )
        except TimeoutException:
            print("❌ No se pudo cargar el video de la clase:", course_url)
            continue

        formatted_index = str(index+1).zfill(2)
        class_title = driver.find_element(By.TAG_NAME, "h1").text
        class_title = sanitize_filename(class_title)
        class_title = f"{formatted_index}_{class_title}"

        time.sleep(8) # Add more time if your internet is slow - necessary to catch requests

        [m3u8_url, ts_urls] = get_ts_urls(driver, downloaded_m3u8_urls)

        if not m3u8_url:
            print("❌ No se encontraron segmentos para la clase:", class_title)
            continue

        downloaded_m3u8_urls.append(m3u8_url)

        print("🔗 Descargando video:", class_title)
        download_all_segments(ts_urls, class_title, course_dir)
        print("🆕 Descarga de video completada")

    # Remove resid segments folder
    segments_dir = os.path.join(course_dir, "segments")
    if os.path.exists(segments_dir):
        os.rmdir(segments_dir)

    print("✅ Descarga del curso completada:", course_title)

    driver.quit()


def download_class(url):
    driver = get_driver()
    driver.get(ROOT_URL)

    load_cookies(driver)
    driver.refresh()  # Refresh to update cookies
    driver.get(url)

    # Wait for the video to load
    try:
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.TAG_NAME, "video"))
        )
    except TimeoutException:
        print("❌ No se pudo cargar el video de la clase:", url)
        driver.quit()

    # Wait until title course is loaded
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
    course_title = driver.find_element(By.TAG_NAME, "h1").text
    course_title = sanitize_filename(course_title)

    time.sleep(8) # Add more time if your internet is slow - necessary to catch requests

    [_, ts_urls] = get_ts_urls(driver, [])

    print("🔗 Descargando clase:", course_title)
    download_all_segments(ts_urls, course_title)
    print("✅ Descarga de clase completada")

    driver.quit()