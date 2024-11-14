import time
import threading
from evdev import InputDevice
from fetch_data import fetch_data  # Mengimpor fungsi fetch_data dari file lain
from read_device import read_device_events  # Mengimpor fungsi read_device_events

# Ganti '/dev/input/eventX' dengan path perangkat input yang sesuai
dev = InputDevice('/dev/input/event4')
print(f"Device {dev.fn} opened")

# URL yang ingin diakses
url = "https://a57f-36-71-172-92.ngrok-free.app/slt/api.php"

# List untuk menyimpan data yang diambil dari API dan status pembacaan input
data = [None]  # Menggunakan list untuk menyimpan data
should_read_input = [False]  # Menggunakan list untuk menyimpan flag pembacaan input

# Menjalankan kedua fungsi dalam thread terpisah
def main():
    # Memulai thread untuk mengambil data
    threading.Thread(target=fetch_data, args=(url, data, should_read_input), daemon=True).start()

    # Menjaga agar program utama tetap berjalan
    while True:
        if data[0] == 1:
            print(".")
        else:
            print("Tidak dapat mengakses scan. Data tidak valid.")
        time.sleep(1)

# Menjalankan program utama
if __name__ == "__main__":
    # Memulai thread untuk membaca perangkat input
    threading.Thread(target=read_device_events, args=(dev, should_read_input), daemon=True).start()
    main()
