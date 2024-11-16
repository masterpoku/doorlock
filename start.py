import time
import threading
import requests
from evdev import InputDevice
from read_device import read_device_events  # Mengimpor fungsi read_device_events

valid_rfid = ['0178526309']  # Daftar RFID yang valid

# Ganti '/dev/input/eventX' dengan path perangkat input yang sesuai
dev = InputDevice('/dev/input/event4')
print(f"Device {dev.fn} opened")

# URL yang ingin diakses
url = "https://287a-36-71-164-132.ngrok-free.app/slt/api.php"

# List untuk menyimpan data yang diambil dari API dan status pembacaan input
data = [None]  # Menggunakan list untuk menyimpan data
should_read_input = [False]  # Menggunakan list untuk menyimpan flag pembacaan input

# Status koneksi
connection_status = False

# Fungsi untuk memeriksa koneksi internet
def is_connected():
    try:
        # Coba akses URL untuk mengecek koneksi
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False

# Fungsi untuk mengambil data dari API
def fetch_data(url, data, should_read_input):
    try:
        # Mengirimkan request GET ke API
        response = requests.get(url, params=data[0] if data[0] else {})
        
        # Jika status kode 200, berarti data berhasil dikirim
        if response.status_code == 200:
            print(f"Data berhasil dikirim: {data[0]}")
            # Update data[0] dengan response JSON atau data baru
            new_data = response.json()  # Jika Anda ingin mengupdate data dengan response
            data[0] = new_data  # Update data[0] dengan data baru
        else:
            data[0] = 2
            print(f"Error: Koneksi gagal dengan status kode {response.status_code}")
        
    except requests.RequestException as e:
        print(f"Terjadi kesalahan saat mengirim request: {e}")

# Menjalankan kedua fungsi dalam thread terpisah
def main():
    global connection_status
    
    while True:
        # Memeriksa koneksi internet
        if is_connected():
            if not connection_status:  # Jika sebelumnya tidak terhubung, dan sekarang terhubung
                print("Koneksi internet terdeteksi, menjalankan fungsi read_device_events...")
                # Memulai thread untuk membaca perangkat input
                threading.Thread(target=read_device_events, args=(dev, should_read_input), daemon=True).start()
                connection_status = True  # Update status koneksi
            # Memulai thread untuk mengambil data dari API
            threading.Thread(target=fetch_data, args=(url, data, should_read_input), daemon=True).start()
        else:
            if connection_status:  # Jika sebelumnya terhubung, tapi sekarang terputus
                print("Koneksi internet terputus, beralih ke valid_rfid...")
                connection_status = False  # Update status koneksi
            print(f"RFID yang valid: {valid_rfid}")
        
        # Tunggu sebelum memeriksa koneksi lagi
        time.sleep(5)

# Menjalankan program utama
if __name__ == "__main__":
    main()
