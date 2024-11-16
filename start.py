import time
import threading
from evdev import InputDevice
import requests
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
            print(f"Error: Koneksi gagal dengan status kode {response.status_code}")
        
    except requests.RequestException as e:
        print(f"Terjadi kesalahan saat mengirim request: {e}")

# Menjalankan kedua fungsi dalam thread terpisah
def main():
    # Memulai thread untuk mengambil data
    threading.Thread(target=fetch_data, args=(url, data, should_read_input), daemon=True).start()

    # Menjaga agar program utama tetap berjalan
    while True:
        if data[0] is not None:  # Memastikan data[0] berisi informasi
            if isinstance(data[0], dict) and 'rfid' in data[0]:  # Memeriksa apakah data[0] adalah dictionary dan memiliki key 'rfid'
                if data[0]['rfid'] in valid_rfid:
                    print(f"RFID {data[0]['rfid']} valid.")
                else:
                    print(f"RFID {data[0]['rfid']} tidak valid.")
            else:
                print("Tidak ada RFID dalam data.")
        else:
            print("Tidak dapat mengakses scan. Data tidak valid.")
        time.sleep(1)

# Menjalankan program utama
if __name__ == "__main__":
    # Memulai thread untuk membaca perangkat input
    threading.Thread(target=read_device_events, args=(dev, should_read_input), daemon=True).start()
    main()
