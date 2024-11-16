import RPi.GPIO as GPIO
from time import sleep

DOOR_SWITCH_PIN = 17  # Pin GPIO untuk sensor pintu
GPIO.setmode(GPIO.BCM)  # Menggunakan nomor pin BCM
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def door_opened(channel):
    print("Pintu terbuka!")

def door_closed(channel):
    print("Pintu tertutup!")

GPIO.add_event_detect(DOOR_SWITCH_PIN, GPIO.BOTH, callback=door_opened, bouncetime=200)
GPIO.add_event_detect(DOOR_SWITCH_PIN, GPIO.FALLING, callback=door_closed, bouncetime=200)

try:
    while True:
        sleep(1)  # Menunggu tanpa henti
except KeyboardInterrupt:
    print("Program dihentikan")
finally:
    GPIO.cleanup()  # Pastikan GPIO dibersihkan saat program selesai
