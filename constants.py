import os
from dotenv import load_dotenv
load_dotenv()

EXEC_MODES = ["login", "download-course", "download-class", "m3u8"]
VALID_EXEC_MODES = "[login | download-course <course_url> | download-class <class_url> | m3u8 <video_name>]"

ROOT_URL = "https://platzi.com"
ROOT_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": f"{ROOT_URL}/",
    "Origin": ROOT_URL,
}

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")