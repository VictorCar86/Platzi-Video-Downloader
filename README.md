# Platzi Video Downloader

## Overview
This Python script is a comprehensive tool for downloading video courses and individual classes from the Platzi platform. It uses Selenium WebDriver for web automation, requests for downloading video segments, and supports various download modes.

## Prerequisites
- Python 3.x
- Google Chrome or Chromium installed
- ChromeDriver in root folder
- Required libraries:
  - `selenium`
  - `seleniumwire`
  - `requests`
  - `python-dotenv`
  - `brotli`

## Environment Setup
1. Create a `.env` file in the project root directory
2. Add the following environment variables:
   ```
   EMAIL=your_platzi_email
   PASSWORD=your_platzi_password
   ```

## Installation
```bash
pip install -r requirements.txt
```

## Execution Modes
The script supports four execution modes:

### 1. Login Mode
```bash
python main.py login
```
- Logs into the Platzi platform
- Saves authentication cookies for subsequent operations

### 2. Download Course Mode
```bash
python main.py download-course <course_url>
```
- Downloads entire course videos
- Creates a directory with the course name
- Saves videos in sequential order

### 3. Download Class Mode
```bash
python main.py download-class <class_url>
```
- Downloads a single class video
- Saves the video in the `output` directory

### 4. M3U8 Download Mode
```bash
python main.py m3u8 [video_name]
```
- Downloads video segments from a local `.m3u8` file
- If no video name is provided, it will prompt the user to enter one

## Key Components

### Main Functions
- `login_platzi()`: Authenticates user on Platzi platform
- `download_course(url)`: Downloads all videos in a course
- `download_class(url)`: Downloads a single class video
- `download_by_m3u8(file_name)`: Downloads video from local `.m3u8` file

### Utility Functions
- `get_ts_urls()`: Extracts video segment URLs from `.m3u8` files
- `download_ts_segment()`: Downloads individual video segments
- `download_all_segments()`: Parallel download and assembly of video segments

## Workflow
1. Authenticate using login mode
2. Use download modes to retrieve videos
3. Videos are saved in the `output` directory

## Limitations
- Requires valid Platzi credentials
- Depends on platform's video streaming structure
- Requires compatible ChromeDriver version

## Error Handling
- Handles various network and download exceptions
- Prints detailed error messages
- Skips problematic video segments

## Security and Performance
- Uses parallel downloads for faster video retrieval
- Manages temporary files and cleanup
- Implements timeout and retry mechanisms

## Troubleshooting
- Verify ChromeDriver compatibility
- Ensure valid Platzi credentials
- Update dependencies if errors occur