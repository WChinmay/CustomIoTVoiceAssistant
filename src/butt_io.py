# Interacting with external button using the GPIO pins on RaspBerry Pi

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

def button_press_callback(channel):
    print("Button was pushed!")

def button_release_callback(channel):
    print("Button was released!")

# GPIO Button Stuff
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

GPIO.add_event_detect(10, GPIO.RISING, callback=button_press_callback) # Setup event on pin 10 rising edge
GPIO.add_event_detect(10, GPIO.FALLING, callback=button_release_callback) # Setup event on pin 10 rising edge


message = input("Press enter to quit\n\n") # Run until someone presses enter
# Cleanup GPIO Button stuff
GPIO.cleanup() # Clean up