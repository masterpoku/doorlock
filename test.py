from evdev import InputDevice, list_devices, categorize, ecodes
from gpiozero import Button, LED
from signal import pause
import threading

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9  # Pin sensor pembukaan pintu (magnetic door switch)
ALARM_PIN = 17       # Pin untuk alarm

# Inisialisasi sensor pintu dan alarm
door_switch = Button(DOOR_SWITCH_PIN)
alarm = LED(ALARM_PIN)  # LED digunakan untuk alarm

# Daftar RFID yang valid
valid_rfid = ['0178526309']

# Status global untuk RFID dan alarm
rfid_valid = False
rfid_scanned = False  # Untuk mengecek apakah RFID telah discan


# Fungsi untuk menemukan perangkat RFID secara dinamis
def find_rfid_device():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "IC Reader" in device.name or "RFID" in device.name:  # Ganti sesuai nama perangkat Anda
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

# Fungsi untuk menangani event pintu terbuka
def door_opened():
    global rfid_valid, rfid_scanned
    print("Pintu terbuka!")

    # Jika RFID belum discan, alarm langsung aktif
    if not rfid_scanned:
        trigger_alarm("Pintu terbuka tanpa RFID!")
    elif not rfid_valid:  # Jika RFID discan tetapi tidak valid
        trigger_alarm("Pintu terbuka dengan RFID tidak valid!")

# Fungsi untuk menangani event pintu tertutup
def door_closed():
    global rfid_valid, rfid_scanned
    print("Pintu tertutup.")
    # Reset status RFID
    rfid_valid = False
    rfid_scanned = False
    disable_alarm()

# Menghubungkan event door_switch dengan fungsi handler
door_switch.when_pressed = door_closed  # Event: Pintu tertutup
door_switch.when_released = door_opened  # Event: Pintu terbuka

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")

    # Menjalankan pembacaan RFID secara paralel
    rfid_thread = threading.Thread(target=read_rfid, daemon=True)
    rfid_thread.start()

    # Stream event-driven dengan pause
    pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
