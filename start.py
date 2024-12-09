from evdev import InputDevice, list_devices, categorize, ecodes
from gpiozero import Button, LED
from signal import pause
import threading
import requests
import time

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9
ALARM_PIN = 18
GAGAL_PIN = 22
PINTU_PIN = 23

# Inisialisasi sensor pintu dan alarm
door_switch = Button(DOOR_SWITCH_PIN)
alarm = LED(ALARM_PIN)
gagal = LED(GAGAL_PIN)
pintu = LED(PINTU_PIN)

# URL API
API_URL = "https://7a72-36-71-167-134.ngrok-free.app/slt/api.php"

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
                        with rfid_lock:
                            rfid_valid_used = True
                            pintu.off()
                            alarm.off()
                    else:
                        print("RFID tidak valid!")
                        pintu.on()
                        gagal.on()
                        time.sleep(1)
                        gagal.off()
                    buffer = ""

# Fungsi untuk menangani event pintu terbuka
def door_opened():
    global rfid_valid_used
    print("Pintu terbuka!")
    if not rfid_valid_used:
        alarm.on()
        print("ALARM AKTIF: Pintu terbuka tanpa izin!")
    else:
        print("Pintu dibuka dengan izin RFID valid.")
        alarm.off()
        rfid_valid_used = False

# Fungsi untuk menangani event pintu tertutup
def door_closed():
    print("Pintu tertutup.")
    pintu.off()
    alarm.off()

# Menghubungkan event door_switch dengan fungsi handler
door_switch.when_pressed = door_closed
door_switch.when_released = door_opened

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")
    valid_rfid = get_valid_rfid_from_api()
    global dev
    dev = find_rfid_device()
    if not dev:
        print("Tidak dapat menemukan perangkat RFID. Pastikan perangkat terhubung.")
        exit(1)
    rfid_thread = threading.Thread(target=read_rfid, args=(valid_rfid,), daemon=True)
    rfid_thread.start()
    pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
