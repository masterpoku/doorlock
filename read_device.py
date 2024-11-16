import time
import requests
from evdev import InputDevice, categorize, ecodes
import threading
import RPi.GPIO as GPIO

# Setup untuk GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup untuk pin sensor pembukaan pintu (magnetic door switch)
DOOR_SWITCH_PIN = 17  # Pin sensor pembukaan pintu (magnetic switch)
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Pin sensor pembukaan pintu

# Daftar RFID yang valid
valid_rfid = ['1234567890', '0987654321']

# Fungsi untuk menampilkan pesan jika pintu dibuka paksa
def handle_force_open():
    print("Pintu dibuka paksa! Proses dihentikan!")

# Fungsi untuk membaca ID RFID dari input perangkat
def read_device_events(dev, should_read_input):
    angka = ""
    while True:
        if should_read_input[0]:  # Cek apakah perangkat input perlu dibaca
            try:
                event = dev.read_one()  # Membaca satu event tanpa memblokir
                if event:
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)

                        if event.value == 1:  # 1 berarti tombol ditekan (down)
                            if key_event.keycode == 'KEY_0':
                                angka += '0'
                            elif key_event.keycode == 'KEY_1':
                                angka += '1'
                            elif key_event.keycode == 'KEY_2':
                                angka += '2'
                            elif key_event.keycode == 'KEY_3':
                                angka += '3'
                            elif key_event.keycode == 'KEY_4':
                                angka += '4'
                            elif key_event.keycode == 'KEY_5':
                                angka += '5'
                            elif key_event.keycode == 'KEY_6':
                                angka += '6'
                            elif key_event.keycode == 'KEY_7':
                                angka += '7'
                            elif key_event.keycode == 'KEY_8':
                                angka += '8'
                            elif key_event.keycode == 'KEY_9':
                                angka += '9'

                    # Jika tombol Enter (KEY_ENTER) ditekan, proses angka yang terkumpul
                    if event.value == 1 and key_event.keycode == 'KEY_ENTER':
                        print(f"ID RFID terkumpul: {angka}")

                        # Validasi apakah ID RFID ada dalam daftar valid
                        if angka not in valid_rfid:
                            print(f"RFID {angka} tidak valid!")
                            angka = ""  # Reset angka setelah diproses
                            continue

                        # Melakukan request GET ke URL dengan parameter 'rfid'
                        try:
                            url = f"https://287a-36-71-164-132.ngrok-free.app/slt/get.php?rfid={angka}"
                            response = requests.get(url)
                            
                            # Cek status kode response dari API
                            if response.status_code == 200:
                                print(f"Data berhasil dikirim: {angka}")
                                if response.json() == 1:
                                    print("Membuka pintu")
                                    open_door()
                                elif response.json() == 2:
                                    print("Registrasi RFID")
                                elif response.json() == 3:
                                    print("Dilarang Masuk Semua RFID")
                                elif response.json() == 4:
                                    print("Pintu Terbuka tanpa RFID")
                                else:
                                    print("Status tidak diketahui")
                            else:
                                print(f"Error: Koneksi gagal dengan status kode {response.status_code}")
                                print(f"RFID {angka} tidak dapat diproses!")

                        except requests.RequestException as e:
                            print(f"Terjadi kesalahan saat mengirim request: {e}")

                        angka = ""  # Reset angka setelah diproses
            except BlockingIOError:
                pass  # Tidak ada event, lanjutkan loop

        else:
            # Tunggu sebentar tanpa memblokir
            time.sleep(0.1)

# Fungsi untuk membuka pintu (simulasi)
def open_door():
    print("Pintu terbuka.")
    # Logika pembukaan pintu bisa ditambahkan di sini (misalnya membuka relay pintu)

# Fungsi untuk memonitor pembukaan pintu paksa menggunakan magnetic door switch
def monitor_for_force_open():
    while True:
        door_status = GPIO.input(DOOR_SWITCH_PIN)
        print(f"Status pintu: {'Tertutup' if door_status == GPIO.LOW else 'Terbuka'}")  # Debugging untuk status pintu
        if door_status == GPIO.HIGH:
            handle_force_open()  # Jika pintu dibuka paksa, tampilkan pesan
        time.sleep(0.1)  # Cek sensor setiap 100ms

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")
    
    # Menjalankan monitoring pembukaan paksa di thread terpisah
    force_open_thread = threading.Thread(target=monitor_for_force_open)
    force_open_thread.daemon = True
    force_open_thread.start()
    
    # Menyiapkan perangkat input
    dev = InputDevice('/dev/input/event0')  # Sesuaikan dengan perangkat input yang Anda gunakan
    should_read_input = [True]  # Variabel untuk mengontrol pembacaan input
    
    # Mulai membaca input dari perangkat
    input_thread = threading.Thread(target=read_device_events, args=(dev, should_read_input))
    input_thread.daemon = True
    input_thread.start()

    # Menunggu input hingga program dihentikan
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
        GPIO.cleanup()

if __name__ == "__main__":
    main()
