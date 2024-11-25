import time
from evdev import InputDevice, categorize, ecodes
import threading
from gpiozero import Button, LED
from signal import pause

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9  # Pin sensor pembukaan pintu (magnetic door switch)
ALARM_PIN = 17       # Pin untuk alarm

# Inisialisasi sensor pintu
door_switch = Button(DOOR_SWITCH_PIN)
alarm = LED(ALARM_PIN)  # LED digunakan untuk alarm

# Daftar RFID yang valid
valid_rfid = ['0178526309']

# Perangkat input RFID (ganti sesuai perangkat Anda)
device_path = '/dev/input/event4'

# Status pintu dan validasi RFID
door_opened_by_valid_rfid = False

# Coba buka perangkat input RFID
try:
    dev = InputDevice(device_path)
    print(f"Device {dev.fn} opened")
except FileNotFoundError:
    print(f"Device not found: {device_path}")
    exit(1)
except PermissionError:
    print(f"Permission denied. Try running with sudo.")
    exit(1)

# Fungsi untuk membuka pintu (simulasi)
def open_door():
    global door_opened_by_valid_rfid
    door_opened_by_valid_rfid = True
    print("Pintu terbuka.")
    time.sleep(5)  # Simulasi waktu pintu terbuka
    door_opened_by_valid_rfid = False
    print("Pintu otomatis tertutup.")

# Fungsi untuk menyalakan alarm
def trigger_alarm():
    print("Pintu dibuka paksa! Alarm aktif!")
    alarm.on()  # Menyalakan alarm
    time.sleep(3)
    alarm.off()  # Mematikan alarm

# Fungsi untuk membaca dan memvalidasi RFID
def read_rfid():
    global door_opened_by_valid_rfid
    print("Tempatkan RFID pada pembaca...")
    buffer = ""  # Buffer untuk menyimpan input RFID sementara
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:  # Hanya event keypress
            key = categorize(event).keycode
            if key.startswith("KEY_"):
                key_char = key.replace("KEY_", "")

                if key_char.isdigit():  # Menambahkan digit ke buffer
                    buffer += key_char
                elif key_char == "ENTER":  # Akhiri input dengan ENTER
                    print(f"ID RFID dibaca: {buffer}")
                    if buffer in valid_rfid:
                        print("RFID valid! Membuka pintu...")
                        open_door()
                    else:
                        print("RFID tidak valid. Alarm tetap aktif.")
                    buffer = ""  # Reset buffer

# Fungsi untuk memonitor pembukaan pintu paksa menggunakan magnetic door switch
def monitor_door():
    global door_opened_by_valid_rfid
    while True:
        if door_switch.is_pressed and not door_opened_by_valid_rfid:
            print("Pintu dibuka tanpa RFID valid!")
            trigger_alarm()
        time.sleep(0.1)  # Cek sensor setiap 100ms

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")

    # Menjalankan monitoring pembukaan paksa di thread terpisah
    monitor_thread = threading.Thread(target=monitor_door)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Mulai pemindaian RFID
    read_rfid()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
