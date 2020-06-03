#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
from printy import printy
import paho.mqtt.client as mqtt

import app_logging
import cli
import powertoggle
import time
import utils
import mqtt_secrets
from fsm import FsmActor

BROKER = "localhost"
PORT = 1883
DEVICE_STATUS = "ON"
MQTT_CLIENT_NAME = "rpi3-proxy-2"


if __name__ == "__main__":
    logger = None
    args = cli.process_cli_args()
    if args.production == True:
        logger = app_logging.setup(
            '/home/david/Moqiott/log/production_{}.log'.format(utils.logname_timestamp()))
    else:
        logger = app_logging.setup(
            '/home/david/Moqiott/log/debug.log')

    logger.info('started APP ' + __name__ + ", time: '{}', Utc: '{}'".format(
        datetime.now(), datetime.utcnow()))
    logger.debug("Starting mqtt client: " + MQTT_CLIENT_NAME)
    client = mqtt.Client(MQTT_CLIENT_NAME)
    client.enable_logger(logger)
    client.username_pw_set(mqtt_secrets.username, mqtt_secrets.password)

    logger.debug("About to connect on: {}:{}".format(BROKER, PORT))
    actor = FsmActor(client)
    actor.start_connection(BROKER, PORT)
    logger.debug("Setting up power pins.")
    powertoggle.setup_pins()

    try:
        client.loop_start()
        while True:
            time.sleep(30)
            actor.send_refresh()
        client.loop_forever()
    except KeyboardInterrupt as e:
        actor.dispose()

    powertoggle.cleanup_pins()
