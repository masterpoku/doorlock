import RPi.GPIO as GPIO
from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import requests
import time
import sys
from RPLCD.i2c import CharLCD
import cv2
import os
from datetime import datetime

# Inisialisasi LCD
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()
lcd.write_string("Sistem Siap!")
time.sleep(2)
lcd.clear()

# Konfigurasi pin GPIO
DOOR_SWITCH_PIN = 9
ALARM_PIN = 4
PINTU_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(ALARM_PIN, GPIO.OUT)
GPIO.setup(PINTU_PIN, GPIO.OUT)

# Fungsi untuk menyalakan pin secara bergantian tiap 3 detik
def cycle_pins_every_3_seconds():
    while True:
        # Nyalakan ALARM_PIN selama 1 detik
        print("Alarm ON")
        GPIO.output(ALARM_PIN, GPIO.HIGH)
        time.sleep(1)
        print("Alarm OFF")
        GPIO.output(ALARM_PIN, GPIO.LOW)

        # Nyalakan PINTU_PIN selama 1 detik
        print("Pintu ON")
        GPIO.output(PINTU_PIN, GPIO.HIGH)
        time.sleep(1)
        print("Pintu OFF")
        GPIO.output(PINTU_PIN, GPIO.LOW)

        # Tunggu 1 detik sebelum mengulang
        time.sleep(1)

# Jalankan thread untuk siklus pin
threading.Thread(target=cycle_pins_every_3_seconds, daemon=True).start()

# Program utama tetap jalan (misalnya tunggu input atau loop lain)
try:
    while True:
        time.sleep(1)  # Bisa diganti logika utama lainnya
except KeyboardInterrupt:
    print("Program dihentikan.")
    GPIO.cleanup()
