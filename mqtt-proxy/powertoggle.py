from gpiozero import LED
# import RPi.GPIO as GPIO
from RPi import _GPIO as GPIO
from time import sleep

import app_logging

REAL_ACTION = False
power_pin = 2

logger = app_logging.get_logger()


def setup_pins():
    GPIO.setmode(GPIO.BCM)
    # , pull_up_down=GPIO.PUD_DOWN
    GPIO.setup(power_pin, GPIO.OUT)
    GPIO.output(power_pin, 1)


def cleanup_pins():
    GPIO.cleanup()


def action_toggle() -> None:
    button = LED(power_pin)
    if REAL_ACTION == True:
        GPIO.output(power_pin, 1)
        sleep(1.5)
        GPIO.output(power_pin, 0)
        sleep(1)
    logger.debug("Tried Power TOGGLE")
    return


def cutoff() -> None:
    button = LED(power_pin)

    if REAL_ACTION == True:
        button.on()
        sleep(5)
        button.off()
        sleep(1)

    logger.debug("Tried Power CUTOFF")
