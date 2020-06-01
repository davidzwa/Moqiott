from gpiozero import LED
import RPi.GPIO as GPIO
from time import sleep

power_pin = 2
GPIO.setmode(GPIO.BCM)
# , pull_up_down=GPIO.PUD_DOWN
GPIO.setup(power_pin, GPIO.OUT)
GPIO.output(power_pin, 1) 

def action_off():
  button = LED(power_pin)
  while True:
      GPIO.output(power_pin, 1)
      sleep(1.5)
      GPIO.output(power_pin, 0)
      sleep(1)
      print("Tried Power-off")
      return

def cutoff():
  button = LED(power_pin)
  while True:
      button.on()
      sleep(5)
      button.off()
      sleep(1)
      
      print("Tried Power-cutoff")
      return