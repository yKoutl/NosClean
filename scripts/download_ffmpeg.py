import urllib.request
import zipfile
import os

url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.4.1/ffmpeg-4.4.1-win-64.zip"
zip_path = "ffmpeg.zip"
target_dir = os.path.abspath("scripts/bin")
os.makedirs(target_dir, exist_ok=True)
ffmpeg_exe = os.path.join(target_dir, "ffmpeg.exe")

if not os.path.exists(ffmpeg_exe):
    print("Downloading lightweight ffmpeg (26MB)...")
    urllib.request.urlretrieve(url, zip_path)
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    if os.path.exists(zip_path):
        os.remove(zip_path)

print("FFmpeg path:", ffmpeg_exe)
print("Exists:", os.path.exists(ffmpeg_exe), "Size:", os.path.getsize(ffmpeg_exe) if os.path.exists(ffmpeg_exe) else 0)
