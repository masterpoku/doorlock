from evdev import InputDevice, list_devices, categorize, ecodes
from gpiozero import Button, LED
from signal import pause
import threading
import requests
import time

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9  # Pin sensor pembukaan pintu (magnetic door switch)
ALARM_PIN = 18       # Pin untuk alarm
GAGAL_PIN = 22       # Pin untuk indikasi RFID salah
PINTU_PIN = 23       # Pin untuk relay pintu

# Inisialisasi sensor pintu dan alarm
door_switch = Button(DOOR_SWITCH_PIN)
alarm = LED(ALARM_PIN)
gagal = LED(GAGAL_PIN)
pintu = LED(PINTU_PIN)  # Pintu dikontrol dengan relay

# URL API
API_URL = "https://7a72-36-71-167-134.ngrok-free.app/slt/api.php"
STATUS_URL = f"{API_URL}?mode=status"

# Variabel global
rfid_valid_used = False
rfid_lock = threading.Lock()

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

# Fungsi untuk menyalakan alarm
def trigger_alarm(reason=""):
    print(f"ALARM AKTIF! {reason}")
    alarm.on()

# Fungsi untuk mematikan alarm
def disable_alarm():
    print("Alarm dimatikan.")
    alarm.off()

# Fungsi untuk memicu indikasi RFID salah
def trigger_gagal(reason=""):
    print(f"RFID SALAH: {reason}")
    gagal.on()
    time.sleep(1)
    gagal.off()

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
                            disable_alarm()
                    else:
                        print("RFID tidak valid!")
                        pintu.on()
                        trigger_gagal("RFID tidak valid.")
                    buffer = ""

# Fungsi untuk menangani event pintu terbuka
def door_opened():
    global rfid_valid_used
    print("Pintu terbuka!")
    if not rfid_valid_used:
        trigger_alarm("Pintu terbuka tanpa izin!")
    else:
        print("Pintu dibuka dengan izin RFID valid.")
        disable_alarm()
        rfid_valid_used = False  # Reset izin setelah pintu terbuka

# Fungsi untuk menangani event pintu tertutup
def door_closed():
    print("Pintu tertutup.")
    pintu.off()
    disable_alarm()

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
