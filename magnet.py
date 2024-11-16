from gpiozero import Button
from signal import pause

DOOR_SWITCH_PIN = 17  # Pin GPIO

# Inisialisasi sensor
door_switch = Button(DOOR_SWITCH_PIN, pull_up=True)

def door_opened():
    print("Pintu terbuka!")

def door_closed():
    print("Pintu tertutup!")

# Deteksi perubahan status pintu
door_switch.when_pressed = door_closed  # LOW
door_switch.when_released = door_opened  # HIGH

print("Monitoring status pintu. Tekan Ctrl+C untuk keluar.")
pause()
