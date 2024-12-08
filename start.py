from evdev import InputDevice, list_devices, categorize, ecodes
from gpiozero import Button, LED
from signal import pause
import threading
import requests

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9  # Pin sensor pembukaan pintu (magnetic door switch)
ALARM_PIN = 17       # Pin untuk alarm

# Inisialisasi sensor pintu dan alarm
door_switch = Button(DOOR_SWITCH_PIN)
alarm = LED(ALARM_PIN)  # LED digunakan untuk alarm

# Status global untuk RFID dan alarm
rfid_valid = False
rfid_scanned = False  # Untuk mengecek apakah RFID telah discan

# URL API
API_URL = "https://d98f-36-71-165-154.ngrok-free.app/slt/api.php"
STATUS_URL = f"{API_URL}?mode=status"

# Fungsi untuk mengambil data RFID valid dari API
def get_valid_rfid_from_api():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                valid_rfid = [item['rfid'] for item in data]
                print(f"Daftar RFID valid: {valid_rfid}")
                return valid_rfid
            else:
                print("Data RFID kosong atau tidak valid.")
                return []
        else:
            print(f"Error: Gagal mendapatkan data (Status Code: {response.status_code})")
            return []
    except Exception as e:
        print(f"Terjadi kesalahan saat mengakses API: {e}")
        return []

# Fungsi untuk mengecek status mode registrasi
def check_registration_mode():
    try:
        response = requests.get(STATUS_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                # Ambil status dari data pertama
                if 'status' in data[0] and data[0]['status'] == 1:
                    print("Mode registrasi RFID baru aktif!")
                    return True
        print("Mode registrasi tidak aktif.")
        return False
    except Exception as e:
        print(f"Terjadi kesalahan saat mengecek status registrasi: {e}")
        return False


# Menyimpan daftar RFID valid
valid_rfid = get_valid_rfid_from_api()

# Fungsi untuk menemukan perangkat RFID secara dinamis
def find_rfid_device():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "IC Reader" in device.name or "RFID" in device.name:
            print(f"RFID device found: {device.name} at {device.path}")
            return device
    print("RFID device not found!")
    return None

# Coba temukan perangkat RFID
dev = find_rfid_device()
if not dev:
    print("Tidak dapat menemukan perangkat RFID. Pastikan perangkat terhubung.")
    exit(1)

# Fungsi untuk menyalakan alarm
def trigger_alarm(reason=""):
    print(f"ALARM AKTIF! {reason}")
    alarm.on()

# Fungsi untuk mematikan alarm
def disable_alarm():
    print("Alarm dimatikan.")
    alarm.off()

# Fungsi untuk membaca dan memvalidasi RFID
def read_rfid():
    global rfid_valid, rfid_scanned

    buffer = ""  # Buffer untuk menyimpan input RFID sementara
    print("Tempatkan RFID pada pembaca...")
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            key = categorize(event).keycode
            if key.startswith("KEY_"):
                key_char = key.replace("KEY_", "")

                if key_char.isdigit():  # Menambahkan digit ke buffer
                    buffer += key_char
                elif key_char == "ENTER":  # Akhiri input dengan ENTER
                    print(f"ID RFID dibaca: {buffer}")
                    rfid_scanned = True
                    if buffer in valid_rfid:
                        print("RFID valid!")
                        rfid_valid = True
                        disable_alarm()
                    else:
                        print("RFID tidak valid.")
                        rfid_valid = False
                        # Periksa mode registrasi
                        if check_registration_mode():
                            print(f"Mode registrasi: Tambahkan RFID baru {buffer} ke sistem.")
                        else:
                            trigger_alarm("RFID tidak valid dan tidak dalam mode registrasi!")
                    buffer = ""  # Reset buffer

# Fungsi untuk menangani event pintu terbuka
def door_opened():
    global rfid_valid, rfid_scanned
    print("Pintu terbuka!")
    if not rfid_scanned:
        trigger_alarm("Pintu terbuka tanpa RFID!")
    elif not rfid_valid:
        trigger_alarm("Pintu terbuka dengan RFID tidak valid!")

# Fungsi untuk menangani event pintu tertutup
def door_closed():
    global rfid_valid, rfid_scanned
    print("Pintu tertutup.")
    rfid_valid = False
    rfid_scanned = False
    disable_alarm()

# Menghubungkan event door_switch dengan fungsi handler
door_switch.when_pressed = door_closed
door_switch.when_released = door_opened

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")
    rfid_thread = threading.Thread(target=read_rfid, daemon=True)
    rfid_thread.start()
    pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
