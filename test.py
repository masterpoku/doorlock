import RPi.GPIO as GPIO
import time
from evdev import InputDevice, categorize, ecodes
import threading

# Daftar RFID yang valid
valid_rfid = ['0178526309']

# Perangkat input RFID (ganti sesuai perangkat Anda)
device_path = '/dev/input/event4'

try:
    dev = InputDevice(device_path)
    print(f"Device {dev.fn} opened")
except FileNotFoundError:
    print(f"Device not found: {device_path}")
    exit(1)
except PermissionError:
    print(f"Permission denied. Try running with sudo.")
    exit(1)

# Setup untuk GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup untuk pin alarm dan sensor pembukaan pintu (magnetic door switch)
ALARM_PIN = 17            # Pin alarm
DOOR_SWITCH_PIN = 27      # Pin sensor pembukaan pintu (disesuaikan dengan wiring Anda)
GPIO.setup(ALARM_PIN, GPIO.OUT)
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Fungsi untuk menyalakan alarm
def trigger_alarm():
    print("Pintu dibuka paksa! Alarm aktif!")
    GPIO.output(ALARM_PIN, GPIO.HIGH)  # Menyalakan alarm
    time.sleep(3)
    GPIO.output(ALARM_PIN, GPIO.LOW)  # Mematikan alarm

# Fungsi untuk membaca dan memvalidasi RFID
def read_rfid():
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
                        print("RFID tidak valid. Coba lagi.")
                    buffer = ""  # Reset buffer

# Fungsi untuk membuka pintu (simulasi)
def open_door():
    print("Pintu terbuka.")
    # Tambahkan logika pembukaan pintu (misalnya mengaktifkan relay)

# Fungsi untuk memonitor pembukaan pintu paksa menggunakan magnetic door switch
def monitor_for_force_open():
    while True:
        if GPIO.input(DOOR_SWITCH_PIN) == GPIO.HIGH:
            print("Pintu dibuka paksa!")
            trigger_alarm()
        time.sleep(0.1)  # Cek sensor setiap 100ms

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")

    # Menjalankan monitoring pembukaan paksa di thread terpisah
    force_open_thread = threading.Thread(target=monitor_for_force_open)
    force_open_thread.daemon = True
    force_open_thread.start()

    # Mulai pemindaian RFID
    read_rfid()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
        GPIO.cleanup()  # Membersihkan konfigurasi GPIO
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        GPIO.cleanup()
