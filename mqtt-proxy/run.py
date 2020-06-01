import paho.mqtt.client as mqtt
import poweroff
from datetime import datetime
from time import sleep

BROKER = "localhost"
PORT = 1883
PROXY = True

TOPIC_STATUS_CLIENT = "pc/status/client"
TOPIC_STATUS_PROXY = "pc/status/proxy"
TOPIC_STATUS = "pc/status"
TOPIC_ACTION_POWER = "pc/action/power"
TOPIC_ACTION_RESULT = "pc/action/result"

DEVICE_STATUS = "ON"
MQTT_CLIENT_NAME = "rpi3-proxy-2"


def pushStatus(client):
    if PROXY:
        client.publish(TOPIC_STATUS_PROXY, "REFRESH proxy")
    else:
        client.publish(TOPIC_STATUS_CLIENT, "REFRESH client ")

def pushAction(client, action):
    if PROXY:
        client.publish(TOPIC_ACTION_RESULT, action)
    else:
        client.publish(TOPIC_ACTION_RESULT, "CLIENT ACTION")


def receiveMessage(client, userdata, message):
    topic = str(message.topic)
    message = str(message.payload.decode("utf-8"))
    pushAction(client, "RX " + topic)
    print("RX topic", topic, "msg ", message)
    if topic == TOPIC_STATUS:
        print("Processing status message")
        pushStatus(client)
        pushAction(client, "STATUS")
    elif topic == TOPIC_ACTION_POWER and PROXY is True:
        print("Powering off")
        pushAction(client, "POWER toggling")
        poweroff.action_off()
        sleep(2.5)
        pushAction(client, "POWER complete")
    else:
        print("Topic unknown: " + message.topic)


def on_connect(client, userdata, flags, rc):
    print("Connected and powered on.")
    client.subscribe(TOPIC_ACTION_POWER)
    client.subscribe(TOPIC_STATUS)
    client.publish("init", str(datetime.now().strftime("%H:%M:%S")))


def on_disconnect(client, userdata, rc):
    print("Disconnect, reason: " + str(rc))
    print("Disconnect, reason: " + str(client))


if __name__ == "__main__":
    print("Starting mqtt client " + MQTT_CLIENT_NAME)
    client = mqtt.Client(MQTT_CLIENT_NAME)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = receiveMessage

    print("about to connect on: " + BROKER)
    client.connect(BROKER, PORT)
    client.loop_forever()
