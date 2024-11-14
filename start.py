import time
import threading
from evdev import InputDevice, categorize, ecodes
from fetch_data import fetch_data  # Mengimpor fungsi fetch_data dari file lain

# Ganti '/dev/input/eventX' dengan path perangkat input yang sesuai
dev = InputDevice('/dev/input/event4')
print(f"Device {dev.fn} opened")

# URL yang ingin diakses
url = "https://a57f-36-71-172-92.ngrok-free.app/slt/api.php"

# List untuk menyimpan data yang diambil dari API dan status pembacaan input
data = [None]  # Menggunakan list untuk menyimpan data
should_read_input = [False]  # Menggunakan list untuk menyimpan flag pembacaan input

# Fungsi untuk membaca event dari perangkat input
def read_device_events():
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
                        print(f"Angka terkumpul: {angka}")
                        angka = ""  # Reset angka setelah diproses
            except BlockingIOError:
                pass  # Tidak ada event, lanjutkan loop

        else:
            time.sleep(1)  # Jika tidak boleh membaca input, tunggu sebentar

# Menjalankan kedua fungsi dalam thread terpisah
def main():
    # Memulai thread untuk mengambil data
    threading.Thread(target=fetch_data, args=(url, data, should_read_input), daemon=True).start()

    # Menjaga agar program utama tetap berjalan
    while True:
        if data[0] == 1:
            print("Standby - Menunggu input dari perangkat.")
        else:
            print("Tidak dapat mengakses scan. Data tidak valid.")
        time.sleep(1)

# Menjalankan program utama
if __name__ == "__main__":
    # Memulai thread untuk membaca perangkat input
    threading.Thread(target=read_device_events, daemon=True).start()
    main()
