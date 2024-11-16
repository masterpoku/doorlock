from gpiozero import Button
from signal import pause

DOOR_SWITCH_PIN = 17  # Pin GPIO

door_switch = Button(DOOR_SWITCH_PIN)

def door_opened():
    print("Pintu terbuka!")

def door_closed():
    print("Pintu tertutup!")

# Menghubungkan fungsi ke sensor
door_switch.when_pressed = door_closed  # LOW
door_switch.when_released = door_opened  # HIGH

print("Monitoring status pintu. Tekan Ctrl+C untuk keluar.")
pause()
