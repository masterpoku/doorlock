import time
import requests
from evdev import InputDevice, categorize, ecodes
import threading


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

                        # Melakukan request GET ke URL dengan parameter 'rfid'
                        try:
                            url = f"https://s287a-36-71-164-132.ngrok-free.app/slt/get.php?rfid={angka}"
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
                                # Jika status bukan 200, lakukan validasi RFID
                                # Daftar RFID yang valid
                                valid_rfid = ['0178526309', '0067545204']

                                if angka in valid_rfid:
                                    print(f"RFID {angka} valid tapi koneksi gagal.")
                                else:
                                    print(f"RFID {angka} tidak valid!")
                                

                        except requests.RequestException as e:
                            print(f"Terjadi kesalahan saat mengirim request: {e}")

                        angka = ""  # Reset angka setelah diproses
            except BlockingIOError:
                pass  # Tidak ada event, lanjutkan loop

        else:
            # Tunggu sebentar tanpa memblokir
            time.sleep(0.1)
