import time
from evdev import InputDevice, categorize, ecodes
import threading
from gpiozero import Button, LED

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9  # Pin sensor pembukaan pintu (magnetic door switch)
ALARM_PIN = 17       # Pin untuk alarm

# Inisialisasi sensor pintu dan alarm
door_switch = Button(DOOR_SWITCH_PIN)
alarm = LED(ALARM_PIN)  # LED digunakan untuk alarm

# Daftar RFID yang valid
valid_rfid = ['0178526309']

# Perangkat input RFID (ganti sesuai perangkat Anda)
device_path = '/dev/input/event4'

# Status pintu dan validasi RFID
rfid_valid = False
rfid_scanned = False  # Untuk mengecek apakah RFID telah discan

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
                    rfid_scanned = True  # Menandakan RFID telah discan
                    if buffer in valid_rfid:
                        print("RFID valid!")
                        rfid_valid = True
                        disable_alarm()  # Matikan alarm jika RFID valid
                    else:
                        print("RFID tidak valid.")
                        rfid_valid = False
                        trigger_alarm("RFID tidak valid.")
                    buffer = ""  # Reset buffer

# Fungsi untuk memonitor pintu
def monitor_door():
    global rfid_valid, rfid_scanned
    while True:
        if door_switch.is_pressed:  # Pintu tertutup
            print("Pintu tertutup.")
            rfid_valid = False  # Reset status RFID saat pintu tertutup
            rfid_scanned = False  # Reset status scan RFID
            disable_alarm()
        else:  # Pintu terbuka
            print("Pintu terbuka!")
            if not rfid_scanned:  # Jika RFID belum discan
                trigger_alarm("Pintu terbuka tanpa RFID!")
            elif not rfid_valid:  # Jika RFID discan tetapi tidak valid
                trigger_alarm("Pintu terbuka dengan RFID tidak valid!")
        time.sleep(0.1)  # Cek sensor setiap 100ms

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")

    # Menjalankan monitoring pintu di thread terpisah
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
