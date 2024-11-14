# read_device.py
from evdev import InputDevice, categorize, ecodes

# Fungsi untuk membaca event dari perangkat input
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
                        print(f"Angka terkumpul: {angka}")
                        angka = ""  # Reset angka setelah diproses
            except BlockingIOError:
                pass  # Tidak ada event, lanjutkan loop

        else:
            time.sleep(1)  # Jika tidak boleh membaca input, tunggu sebentar
