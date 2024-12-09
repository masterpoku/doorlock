import RPi.GPIO as GPIO
import time

# Set up GPIO mode to BCM (Broadcom pin numbering)
GPIO.setmode(GPIO.BCM)

# Set GPIO4 as output (the GPIO pin to which the relay is connected)
relay_pin = 4
GPIO.setup(relay_pin, GPIO.OUT)

# Function to turn relay on
def relay_on():
    GPIO.output(relay_pin, GPIO.HIGH)
    print("Relay is ON")

# Function to turn relay off
def relay_off():
    GPIO.output(relay_pin, GPIO.LOW)
    print("Relay is OFF")

try:
    while True:
        # Turn relay on for 5 seconds
        relay_on()
        time.sleep(5)  # Relay on for 5 seconds

        # Turn relay off for 5 seconds
        relay_off()
        time.sleep(5)  # Relay off for 5 seconds

except KeyboardInterrupt:
    print("Program interrupted")
finally:
    GPIO.cleanup()  # Clean up GPIO settings when the program ends
