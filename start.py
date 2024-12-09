import RPi.GPIO as GPIO
from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import requests
import time
import sys

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
API_URL = "https://7a72-36-71-167-134.ngrok-free.app/slt/api.php"
MODE = "https://7a72-36-71-167-134.ngrok-free.app/slt/api.php?mode"
REGISTRASI = "https://7a72-36-71-167-134.ngrok-free.app/slt/registrasi.php?rfid={rfid}"
LOG = "https://7a72-36-71-167-134.ngrok-free.app/slt/log.php?rfid={rfid}"

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
        return []

# Fungsi untuk membaca dan memvalidasi RFID
def read_rfid(valid_rfid):
    global rfid_valid_used
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
                        GPIO.output(PINTU_PIN, GPIO.LOW)  # Buka pintu
                        GPIO.output(ALARM_PIN, GPIO.LOW)  # Matikan alarm
                        with rfid_lock:
                            rfid_valid_used = True
                        # Log RFID ke API
                        try:
                            log_url = LOG.format(rfid=buffer)
                            response = requests.get(log_url, timeout=10)
                            response.raise_for_status()
                            print(f"RFID {buffer} telah dicatat ke log.")
                        except requests.RequestException as e:
                            print(f"Kesalahan saat mencatat log RFID: {e}")
                        break  # Setelah valid, keluar dari loop dan berhenti
                    else:
                        print("RFID tidak valid!")
                        # Mengecek request mode dan jika status = 1, lakukan registrasi
                        try:
                            response = requests.get(MODE, timeout=10)
                            response.raise_for_status()
                            mode_data = response.json()
                            if isinstance(mode_data, list) and any(entry.get('status') == 1 for entry in mode_data):
                                # Jika status = 1, lakukan registrasi RFID
                                registrasi_url = REGISTRASI.format(rfid=buffer)
                                registrasi_response = requests.get(registrasi_url, timeout=10)
                                registrasi_response.raise_for_status()
                                print(f"RFID {buffer} telah berhasil didaftarkan.")
                            else:
                                print("Status bukan 1, tidak melakukan registrasi.")
                        except requests.RequestException as e:
                            print(f"Kesalahan saat mengakses API: {e}")
                        GPIO.output(PINTU_PIN, GPIO.HIGH)  # Tetap tutup
                    buffer = ""

# Fungsi untuk menangani event pintu terbuka
def door_opened():
    global rfid_valid_used
    print("Pintu terbuka!")
    if not rfid_valid_used:
        print("ALARM AKTIF: Pintu terbuka tanpa izin!")
        GPIO.output(ALARM_PIN, GPIO.HIGH)  # Nyalakan alarm
    else:
        print("Pintu dibuka dengan izin RFID valid.")
        GPIO.output(ALARM_PIN, GPIO.LOW)  # Matikan alarm
        rfid_valid_used = False

# Fungsi untuk menangani event pintu tertutup
def door_closed():
    print("Pintu tertutup.")
    GPIO.output(PINTU_PIN, GPIO.LOW)  # Tutup pintu
    GPIO.output(ALARM_PIN, GPIO.LOW)  # Matikan alarm

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")
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
