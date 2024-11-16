import RPi.GPIO as GPIO
import time

# Konfigurasi GPIO pin
DOOR_SWITCH_PIN = 17  # Ganti dengan pin yang sesuai dengan koneksi Anda

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)  # Gunakan skema penomoran BCM
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up untuk sinyal stabil

def door_status_changed(channel):
    if GPIO.input(DOOR_SWITCH_PIN):  # HIGH berarti pintu terbuka (tergantung konfigurasi sensor)
        print("Pintu terbuka!")
    else:  # LOW berarti pintu tertutup
        print("Pintu tertutup!")

# Deteksi perubahan status pintu dengan interrupt
GPIO.add_event_detect(DOOR_SWITCH_PIN, GPIO.BOTH, callback=door_status_changed, bouncetime=200)

print("Monitoring status pintu. Tekan Ctrl+C untuk keluar.")
try:
    while True:
        time.sleep(1)  # Loop agar program tetap berjalan
except KeyboardInterrupt:
    print("\nProgram dihentikan.")
finally:
    GPIO.cleanup()  # Membersihkan konfigurasi GPIO
