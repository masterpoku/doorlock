import cv2
import os
from datetime import datetime

# Buat folder image kalau belum ada
os.makedirs("image", exist_ok=True)

# Ambil waktu sekarang
filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
filepath = os.path.join("image", filename)

# Buka kamera (0 biasanya /dev/video0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Gagal membuka kamera.")
else:
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filepath, frame)
        print(f"Gambar disimpan di: {filepath}")
    else:
        print("Gagal mengambil gambar.")
    cap.release()
