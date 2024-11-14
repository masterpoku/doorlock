import requests
import time
from evdev import InputDevice, categorize, ecodes
import threading

# Ganti '/dev/input/eventX' dengan path perangkat input yang sesuai
dev = InputDevice('/dev/input/event4')
print(f"Device {dev.fn} opened")

# URL yang ingin diakses
url = "https://a57f-36-71-172-92.ngrok-free.app/slt/api.php"

# Variable untuk menyimpan data yang diambil dari API
data = None
# Flag untuk mengontrol apakah pembacaan input perlu dimulai atau dihentikan
should_read_input = False

# Fungsi untuk mengambil data secara berkala
def fetch_data():
    global data, should_read_input
    while True:
        try:
            # Mengirimkan GET request
            response = requests.get(url)

            # Mengecek status code untuk memastikan permintaan berhasil
            if response.status_code == 200:
                new_data = response.json()
                if new_data != data:  # Periksa perubahan status data
                    print("Data berhasil diperbarui:", new_data)
                    data = new_data

                    # Atur flag untuk mulai atau berhenti membaca perangkat input
                    if data == 1:
                        if not should_read_input:
                            print("Data = 1, mulai membaca input...")
                            should_read_input = True
                    else:
                        if should_read_input:
                            print("Data != 1, hentikan membaca input...")
                            should_read_input = False

            else:
                print(f"Gagal mendapatkan data. Status code: {response.status_code}")

        except Exception as e:
            print(f"Terjadi kesalahan saat mengambil data: {e}")

        # Menunggu selama 10 detik sebelum mengirim request lagi
        time.sleep(10)

# Fungsi untuk membaca event dari perangkat input
def read_device_events():
    angka = ""
    while True:
        if should_read_input:  # Cek apakah perangkat input perlu dibaca
            for event in dev.read():
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
        else:
            time.sleep(1)  # Jika tidak boleh membaca input, tunggu sebentar

# Menjalankan kedua fungsi dalam thread terpisah
def main():
    # Memulai thread untuk mengambil data
    threading.Thread(target=fetch_data, daemon=True).start()

    # Menjaga agar program utama tetap berjalan
    while True:
        if data == 1:
            print("Standby - Menunggu input dari perangkat.")
        else:
            print("Tidak dapat mengakses scan. Data tidak valid.")
        time.sleep(1)

# Menjalankan program utama
if __name__ == "__main__":
    # Memulai thread untuk membaca perangkat input
    threading.Thread(target=read_device_events, daemon=True).start()
    main()
