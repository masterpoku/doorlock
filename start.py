import time
import requests
import threading
from evdev import InputDevice, categorize, ecodes
from gpiozero import Button, LED  # Menambahkan LED untuk indikator
from signal import pause


DOOR_SWITCH_PIN = 17  # Pin GPIO untuk sensor pintu
INDICATOR_PIN = 17    # Pin GPIO untuk indikator pintu terbuka paksa

door_switch = Button(DOOR_SWITCH_PIN)
indicator = LED(INDICATOR_PIN)  # Menyalakan LED di pin ini sebagai indikator

def door_opened():
    print("Pintu terbuka! Paksa!")
    indicator.on()  # Menyalakan LED sebagai indikator pintu dibuka paksa
    # Menampilkan alarm jika pintu terbuka tanpa RFID
    print("Alarm: Pintu terbuka tanpa RFID!")

def door_closed():
    print("Pintu tertutup!")
    indicator.off()  # Mematikan LED ketika pintu tertutup

# Menghubungkan fungsi ke sensor pintu
door_switch.when_pressed = door_closed  # LOW
door_switch.when_released = door_opened  # HIGH

valid_rfid = ['0178526309']  # Daftar RFID yang valid
dev = InputDevice('/dev/input/event4')  # Ganti dengan perangkat input yang sesuai
print(f"Device {dev.fn} opened")

url = "https://287a-36-71-164-132.ngrok-free.app/slt/get.php"

data = [None]
should_read_input = [False]

# Status koneksi
connection_status = False
rfid_data = ""  # Menyimpan data RFID yang terkumpul

# Fungsi untuk memeriksa koneksi internet
def is_connected():
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Fungsi untuk mengambil data dari API dan memverifikasi RFID
def fetch_data_from_api(rfid):
    try:
        response = requests.get(f"{url}?rfid={rfid}")
        if response.status_code == 200:
            try:
                status = response.json()  # Coba untuk mengonversi respons ke JSON
                if status == 1:
                    print("Membuka pintu")
                elif status == 2:
                    print("Registrasi RFID")
                elif status == 3:
                    print("Dilarang Masuk Semua RFID")
                elif status == 4:
                    print("Pintu Terbuka tanpa RFID")
                    # Alarm jika pintu terbuka tanpa RFID
                    print("Alarm: Pintu terbuka tanpa RFID!")
                else:
                    print("Status tidak diketahui")
            except ValueError:  # Jika respons tidak valid sebagai JSON
                print(f"Kesalahan: Respons tidak dapat dikonversi ke JSON. Konten: {response.text}")
        else:
            print(f"Error: Koneksi gagal dengan status kode {response.status_code}")
    except requests.RequestException as e:
        print(f"Terjadi kesalahan saat mengirim request: {e}")

# Fungsi untuk membaca ID RFID dari input perangkat
def read_device_events(dev, should_read_input):
    global rfid_data
    while True:
        if should_read_input[0]:
            try:
                event = dev.read_one()  # Membaca satu event tanpa memblokir
                if event:
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)
                        if event.value == 1:  # Jika tombol ditekan
                            if key_event.keycode in ['KEY_0', 'KEY_1', 'KEY_2', 'KEY_3', 'KEY_4', 'KEY_5', 'KEY_6', 'KEY_7', 'KEY_8', 'KEY_9']:
                                rfid_data += key_event.keycode[-1]  # Mengambil angka dari keycode

                    # Jika tombol Enter ditekan
                    if event.value == 1 and key_event.keycode == 'KEY_ENTER':
                        print(f"ID RFID terkumpul: {rfid_data}")
                        if connection_status:
                            fetch_data_from_api(rfid_data)  # Mengambil data dari API jika koneksi ada
                        else:
                            print(f"Data RFID pasif: {rfid_data}")  # Gunakan data RFID secara pasif
                        rfid_data = ""  # Reset setelah diproses
            except BlockingIOError:
                pass  # Tidak ada event, lanjutkan loop
        else:
            time.sleep(0.1)

# Fungsi untuk memeriksa koneksi dan mengelola logika pembacaan RFID
def main():
    global connection_status, should_read_input

    while True:
        if is_connected():
            if not connection_status:
                print("Koneksi internet terdeteksi, melanjutkan pengecekan data RFID...")
                # Jika koneksi pulih, mulai membaca input RFID
                should_read_input[0] = True
                connection_status = True
        else:
            if connection_status:
                print("Koneksi internet terputus, menggunakan data RFID pasif...")
                should_read_input[0] = True  # Tetap membaca input RFID meskipun tidak ada koneksi
                connection_status = False

        # Tunggu sebelum memeriksa koneksi lagi
        time.sleep(5)

if __name__ == "__main__":
    # Menjalankan fungsi pembacaan perangkat input di thread terpisah
    threading.Thread(target=read_device_events, args=(dev, should_read_input), daemon=True).start()

    # Menjalankan program utama
    main()
