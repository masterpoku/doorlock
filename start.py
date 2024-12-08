import RPi.GPIO as GPIO
from evdev import InputDevice, list_devices, categorize, ecodes
from signal import pause
import threading
import requests
import time

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9  # Pin sensor pembukaan pintu (magnetic door switch)
ALARM_PIN = 18       # Pin untuk alarm
DOOR_PIN = 22        # Pin untuk kunci pintu
CAMERA_PIN = 23      # Pin untuk kamera

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ALARM_PIN, GPIO.OUT)
GPIO.setup(DOOR_PIN, GPIO.OUT)
GPIO.setup(CAMERA_PIN, GPIO.OUT)

# URL API
API_URL = "https://18c7-182-1-97-30.ngrok-free.app/slt/api.php"
STATUS_URL = f"{API_URL}?mode=status"

# Fungsi kontrol GPIO
def buka_pintu():
    print("Pintu terbuka.")
    GPIO.output(DOOR_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(DOOR_PIN, GPIO.LOW)

def trigger_alarm(reason=""):
    print(f"ALARM AKTIF! {reason}")
    GPIO.output(ALARM_PIN, GPIO.HIGH)

def disable_alarm():
    print("Alarm dimatikan.")
    GPIO.output(ALARM_PIN, GPIO.LOW)

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
        print(f"Terjadi kesalahan saat mengakses API: {e}")
        return []

# Fungsi untuk mendaftarkan RFID baru ke API
def register_new_rfid(rfid):
    try:
        url = f"https://18c7-182-1-97-30.ngrok-free.app/slt/registrasi.php?rfid={rfid}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"RFID {rfid} berhasil didaftarkan!")
    except requests.RequestException as e:
        print(f"Terjadi kesalahan saat mendaftarkan RFID: {e}")

# Fungsi untuk mengecek status mode registrasi
def check_registration_mode():
    try:
        response = requests.get(STATUS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get('status', 0)
        print("Mode registrasi tidak aktif atau data kosong.")
        return 0
    except requests.RequestException as e:
        print(f"Terjadi kesalahan saat mengecek status registrasi: {e}")
        return 0

# Fungsi untuk menemukan perangkat RFID secara dinamis
def find_rfid_device():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "IC Reader" in device.name or "RFID" in device.name:
            print(f"RFID device found: {device.name} at {device.path}")
            return device
    print("RFID device not found!")
    return None

# Fungsi untuk membaca dan memvalidasi RFID
def read_rfid(valid_rfid):
    dev = find_rfid_device()
    if not dev:
        print("Tidak dapat menemukan perangkat RFID. Pastikan perangkat terhubung.")
        return

    buffer = ""
    print("Tempatkan RFID pada pembaca...")
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            key = categorize(event).keycode
            if key.startswith("KEY_"):
                key_char = key.replace("KEY_", "")
                if key_char.isdigit():
                    buffer += key_char
                elif key_char == "ENTER":
                    print(f"ID RFID dibaca: {buffer}")
                    if buffer in valid_rfid:
                        print("RFID valid!")
                        buka_pintu()
                        disable_alarm()
                    else:
                        print("RFID tidak valid.")
                        status = check_registration_mode()
                        if status == 1:
                            register_new_rfid(buffer)
                            valid_rfid.append(buffer)
                        elif status == 3:
                            print("Mode kunci aktif. Akses ditolak.")
                        else:
                            trigger_alarm("RFID tidak valid!")
                    buffer = ""

# Fungsi untuk menangani event pintu terbuka
def door_opened():
    print("Pintu terbuka tanpa otorisasi!")
    trigger_alarm()

# Fungsi untuk menangani event pintu tertutup
def door_closed():
    print("Pintu tertutup.")
    disable_alarm()

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")
    valid_rfid = get_valid_rfid_from_api()
    threading.Thread(target=read_rfid, args=(valid_rfid,), daemon=True).start()
    GPIO.add_event_detect(DOOR_SWITCH_PIN, GPIO.FALLING, callback=lambda x: door_opened(), bouncetime=300)
    GPIO.add_event_detect(DOOR_SWITCH_PIN, GPIO.RISING, callback=lambda x: door_closed(), bouncetime=300)
    pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
        GPIO.cleanup()
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        GPIO.cleanup()
