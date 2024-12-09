from evdev import InputDevice, list_devices, categorize, ecodes
import RPi.GPIO as GPIO
import time


# Set up GPIO mode to BCM (Broadcom pin numbering)
GPIO.setmode(GPIO.BCM)
# Set GPIO18 as output (the GPIO pin to which the relay is connected)
relay_pin = 25
GPIO.setup(relay_pin, GPIO.OUT)
def relay_off():
    GPIO.output(relay_pin, GPIO.LOW)
    print("Relay is OFF")
def relay_on():
    GPIO.output(relay_pin, GPIO.HIGH)
    print("Relay is ON")

# Daftar RFID valid
VALID_RFID = ["0178526309"]

# Fungsi untuk menemukan perangkat RFID secara dinamis
def find_rfid_device():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "IC Reader" in device.name or "RFID" in device.name:
            print(f"RFID device found: {device.name} at {device.path}")
            return device
    print("RFID device not found!")
    return None

# Fungsi untuk membaca dan memvalidasi RFID
def read_rfid():
    dev = find_rfid_device()
    if not dev:
        print("Tidak dapat menemukan perangkat RFID. Pastikan perangkat terhubung.")
        return

    buffer = ""
    print("Tempatkan RFID pada pembaca...")
    relay_off()
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            key = categorize(event).keycode
            if key.startswith("KEY_"):
                key_char = key.replace("KEY_", "")
                if key_char.isdigit():
                    buffer += key_char
                elif key_char == "ENTER":
                    print(f"ID RFID dibaca: {buffer}")
                    if buffer in VALID_RFID:

                        # Turn relay on for 5 seconds
                        relay_on()
                        time.sleep(1)

                        # Turn relay off
                        relay_off()

                        print("RFID valid! Pintu terbuka.")
                    else:
                        print("RFID tidak valid! Akses ditolak.")
                    buffer = ""  # Reset buffer setelah membaca

if __name__ == "__main__":
    try:
        read_rfid()
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
