import RPi.GPIO as GPIO
from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import requests
import time
import sys
from RPLCD.i2c import CharLCD
import cv2
import os
from datetime import datetime

# Folder containing images
IMAGE_FOLDER = "image"

# API endpoint for uploading images
UPLOAD_URL = "https://sikapngalah.com/rfid/upload.php"

# Inisialisasi LCD
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()
lcd.write_string("Sistem Siap!")
time.sleep(2)
lcd.clear()

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9
ALARM_PIN = 4
PINTU_PIN = 27

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Door switch as input with pull-up
GPIO.setup(ALARM_PIN, GPIO.OUT)  # Alarm as output
GPIO.setup(PINTU_PIN, GPIO.OUT)  # Pintu relay as output

# URL API
API_URL = "https://sikapngalah.com/rfid/api.php"
MODE = "https://sikapngalah.com/rfid/api.php?mode"
REGISTRASI = "https://sikapngalah.com/rfid/registrasi.php?rfid={rfid}"
LOG = "https://sikapngalah.com/rfid/log.php?rfid={rfid}"

# Variabel global
rfid_valid_used = False
rfid_lock = threading.Lock()

# Fungsi untuk menemukan perangkat RFID secara dinamis
def find_rfid_device():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "IC Reader" in device.name or "RFID" in device.name:
            print(f"RFID device found: {device.name} at {device.path}")
            return device
    print("RFID device not found!")
    lcd.write_string("RFID Not Found!")
    return None

# Fungsi untuk mengambil data RFID valid dari API
def get_valid_rfid_from_api():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            valid_rfid = [item['rfid'] for item in data]
            print(f"Daftar RFID valid: {valid_rfid}")
            return valid_rfid
        else:
            print("Data RFID kosong atau tidak valid.")
            return []
    except requests.RequestException as e:
        print(f"Kesalahan saat mengakses API: {e}")
        lcd.write_string("API Error!")
        return []

# Fungsi untuk membaca dan memvalidasi RFID
def read_rfid(valid_rfid):
    global rfid_valid_used
    buffer = ""
    print("Tempatkan RFID pada pembaca...")
    lcd.write_string("Scan RFID...")
    time.sleep(1)
    lcd.clear()
    
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            key = categorize(event).keycode
            if key.startswith("KEY_"):
                key_char = key.replace("KEY_", "")
                if key_char.isdigit():
                    buffer += key_char
                elif key_char == "ENTER":
                    print(f"ID RFID dibaca: {buffer}")
                    lcd.clear()
                    lcd.write_string(f"RFID: {buffer}")
                    time.sleep(1)
                    if buffer in valid_rfid:
                        print("RFID valid!")
                        lcd.clear()
                        lcd.write_string('RFID Valid!')
                        GPIO.output(PINTU_PIN, GPIO.LOW)  # Buka pintu
                        GPIO.output(ALARM_PIN, GPIO.LOW)  # Matikan alarm
                        capture_image(buffer)
                        with rfid_lock:
                            rfid_valid_used = True
                    else:
                        print("RFID tidak valid!")
                        lcd.clear()
                        lcd.write_string("RFID Invalid!")
                        capture_image(buffer)
                        time.sleep(1)
                        # Mengecek request mode dan jika status = 1, lakukan registrasi
                        try:
                            response = requests.get(MODE, timeout=10)
                            response.raise_for_status()
                            mode_data = response.json()
                            if isinstance(mode_data, list) and any(entry.get('status') == "1" for entry in mode_data):
                                # Jika status = 1, lakukan registrasi RFID
                                registrasi_url = REGISTRASI.format(rfid=buffer)
                                registrasi_response = requests.get(registrasi_url, timeout=10)
                                registrasi_response.raise_for_status()
                                lcd.write_string("RFID Registered!")
                                print(f"RFID {buffer} telah berhasil didaftarkan.")
                                valid_rfid = get_valid_rfid_from_api()
                                break
                            else:
                                lcd.clear()
                                lcd.write_string("No Reg Allowed")
                        except requests.RequestException as e:
                            print(f"Kesalahan saat mengakses API: {e}")
                            lcd.write_string("API Error!")
                        GPIO.output(PINTU_PIN, GPIO.HIGH)  # Tetap tutup
                    buffer = ""

def capture_image(nama):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{nama}_{timestamp}.jpg"
    filepath = os.path.join(IMAGE_FOLDER, filename)

    # Buka kamera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Gagal buka kamera.")
        return

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Gagal ambil gambar.")
        return

    # Simpan gambar
    try:
        cv2.imwrite(filepath, frame)
        print(f"📸 Gambar disimpan sebagai: {filepath}")
    except Exception as e:
        print(f"❌ Error saat menyimpan gambar: {e}")
        return

    # Log nama ke API
    try:
        log_url = LOG_URL.format(rfid=nama)
        response = requests.get(log_url, timeout=10)
        response.raise_for_status()
        print(f"✅ Nama {nama} telah dicatat ke log.")
    except requests.RequestException as e:
        print(f"❌ Kesalahan saat mencatat log nama: {e}")

    # Upload gambar ke server
    try:
        with open(filepath, 'rb') as file:
            files = {'file': file}
            response = requests.post(UPLOAD_URL, files=files, timeout=20)
            if response.status_code == 200:
                print(f"✅ Upload sukses: {response.json()}")
            else:
                print(f"❌ Gagal upload. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error saat upload: {e}")
def door_opened():
    global rfid_valid_used
    print("Pintu terbuka!")
    lcd.clear()
    lcd.write_string("Pintu Terbuka!")

    if not rfid_valid_used:
        print("ALARM AKTIF: Pintu terbuka tanpa izin!")
        lcd.write_string("ALARM!")
        GPIO.output(ALARM_PIN, GPIO.HIGH)
        capture_image("alm_aktif")
    else:
        print("Pintu dibuka dengan izin RFID valid.")
        GPIO.output(ALARM_PIN, GPIO.LOW)
        capture_image("rfid_valid")
        rfid_valid_used = False

# Fungsi untuk menangani event pintu tertutup
def door_closed():
    print("Pintu tertutup.")
    lcd.clear()
    lcd.write_string("Pintu Tertutup")
    GPIO.output(PINTU_PIN, GPIO.LOW)  # Tutup pintu
    GPIO.output(ALARM_PIN, GPIO.LOW)  # Matikan alarm

# Fungsi utama
def main():
    door_closed()
    print("Sistem Doorlock Aktif")
    lcd.write_string("Sistem Aktif")
    valid_rfid = get_valid_rfid_from_api()
    global dev
    dev = find_rfid_device()
    if not dev:
        print("Tidak dapat menemukan perangkat RFID. Pastikan perangkat terhubung.")
        exit(1)

    # Monitor pintu menggunakan thread
    def door_monitor():
        previous_state = GPIO.input(DOOR_SWITCH_PIN)
        while True:
            current_state = GPIO.input(DOOR_SWITCH_PIN)
            if current_state != previous_state:
                if current_state == GPIO.HIGH:
                    door_opened()
                else:
                    door_closed()
                previous_state = current_state
            time.sleep(0.1)

    threading.Thread(target=door_monitor, daemon=True).start()

    # RFID reading
    rfid_thread = threading.Thread(target=read_rfid, args=(valid_rfid,), daemon=True)
    rfid_thread.start()

    try:
        while True:
            time.sleep(1)
            if rfid_valid_used:
                print("RFID valid. Program selesai.")
                GPIO.cleanup()  # Bersihkan GPIO dan keluar dari program
                sys.exit(0)  # Keluar dari program
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
        GPIO.cleanup()
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        GPIO.cleanup()

if __name__ == "__main__":
    main()
