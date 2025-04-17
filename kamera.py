import cv2
import os
import requests
from datetime import datetime

# Folder dan URL
IMAGE_FOLDER = "image"
UPLOAD_URL = "https://sikapngalah.com/rfid/upload.php"

# Bikin folder kalau belum ada
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def capture_image(nama):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{nama}_{timestamp}.jpg"
    filepath = os.path.join(IMAGE_FOLDER, filename)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Gagal buka kamera.")
        return None

    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(filepath, frame)
        print(f"📸 Disimpan sebagai: {filepath}")
        return filepath
    else:
        print("❌ Gagal ambil gambar.")
        return None

def upload_image(image_path):
    try:
        with open(image_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(UPLOAD_URL, files=files)
            if response.status_code == 200:
                print(f"✅ Upload sukses: {response.json()}")
            else:
                print(f"❌ Gagal upload. Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error saat upload: {e}")

if __name__ == "__main__":
    nama = "agus"  # Ganti sesuai nama lo
    image_path = capture_image(nama)
    if image_path:
        upload_image(image_path)
