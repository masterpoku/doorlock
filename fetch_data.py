# fetch_data.py
import requests
import time

# Fungsi untuk mengambil data secara berkala
def fetch_data(url, data, should_read_input):
    while True:
        try:
            # Mengirimkan GET request
            response = requests.get(url)

            # Mengecek status code untuk memastikan permintaan berhasil
            if response.status_code == 200:
                new_data = response.json()
                if new_data != data[0]:  # Periksa perubahan status data
                    print("Data berhasil diperbarui:", new_data)
                    data[0] = new_data  # Mengubah nilai data

                    # Atur flag untuk mulai atau berhenti membaca perangkat input
                    if data[0] == 1:
                        if not should_read_input[0]:
                            print("Data = 1, mulai membaca input...")
                            should_read_input[0] = True
                    else:
                        if should_read_input[0]:
                            print("Data != 1, hentikan membaca input...")
                            should_read_input[0] = False

            else:
                print(f"Gagal mendapatkan data. Status code: {response.status_code}")

        except Exception as e:
            print(f"Terjadi kesalahan saat mengambil data: {e}")

        # Menunggu selama 10 detik sebelum mengirim request lagi
        time.sleep(10)
