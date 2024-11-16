import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
import threading

# Setup untuk GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup untuk pin alarm dan sensor pembukaan pintu (magnetic door switch)
ALARM_PIN = 17            # Pin alarm (sama dengan sensor)
DOOR_SWITCH_PIN = 17      # Pin sensor pembukaan pintu (magnetic switch)
GPIO.setup(ALARM_PIN, GPIO.OUT)  # Pin alarm
GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Pin sensor pembukaan pintu

# Dummy data RFID valid (misalnya, ID RFID yang valid)
valid_rfid = [1234567890]

# Fungsi untuk menyalakan alarm
def trigger_alarm():
    print("Pintu dibuka paksa! Alarm aktif!")
    GPIO.output(ALARM_PIN, GPIO.HIGH)  # Menyalakan alarm
    time.sleep(3)
    GPIO.output(ALARM_PIN, GPIO.LOW)  # Mematikan alarm

# Fungsi untuk membaca dan memvalidasi RFID
def read_rfid():
    reader = SimpleMFRC522()
    print("Tempatkan RFID pada pembaca...")
    
    while True:
        id, text = reader.read()
        print(f"ID RFID dibaca: {id}")
        
        if id in valid_rfid:
            print("RFID valid! Membuka pintu...")
            open_door()
        else:
            print("RFID tidak valid. Coba lagi.")
        
        time.sleep(1)  # Tunggu sebentar sebelum memulai pemindaian lagi

# Fungsi untuk membuka pintu (simulasi)
def open_door():
    print("Pintu terbuka.")
    # Logika pembukaan pintu bisa ditambahkan di sini (misalnya membuka relay pintu)

# Fungsi untuk memonitor pembukaan pintu paksa menggunakan magnetic door switch
def monitor_for_force_open():
    while True:
        if GPIO.input(DOOR_SWITCH_PIN) == GPIO.HIGH:
            trigger_alarm()  # Deteksi pembukaan pintu paksa
        time.sleep(0.1)  # Cek sensor setiap 100ms

# Fungsi utama
def main():
    print("Sistem Doorlock Aktif")
    
    # Menjalankan monitoring pembukaan paksa di thread terpisah
    force_open_thread = threading.Thread(target=monitor_for_force_open)
    force_open_thread.daemon = True
    force_open_thread.start()
    
    # Mulai pemindaian RFID
    read_rfid()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistem dihentikan.")
        GPIO.cleanup()
