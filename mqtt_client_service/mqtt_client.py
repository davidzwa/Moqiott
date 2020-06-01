import paho.mqtt.client as mqtt
import time
BROKER = "10.0.4.35"
PORT = 1883
PROXY = False

TOPIC_STATUS_CLIENT = "pc/status/client"
TOPIC_STATUS_PROXY = "pc/status/proxy"
TOPIC_STATUS = "pc/status"
TOPIC_ACTION_ON = "pc/action/poweron"
TOPIC_ACTION_OFF = "pc/action/poweroff"
TOPIC_ACTION_RESULT = "pc/action/result"

DEVICE_STATUS = "ON"
MQTT_CLIENT_NAME = "pc-mqtt-docker"


def pushStatus(client):
    if PROXY:
        print("Publishing proxy status")
        client.publish(TOPIC_STATUS_PROXY, DEVICE_STATUS)
    else:
        client.publish(TOPIC_STATUS_CLIENT, "REFRESHING")
        print("Publishing client status")
        time.sleep(0.2)
        client.publish(TOPIC_STATUS_CLIENT, DEVICE_STATUS)


def receiveMessage(client, userdata, message):
    topic = str(message.topic)
    message = str(message.payload.decode("utf-8"))
    print("Received msg:", topic + " " + message)
    if topic == TOPIC_STATUS:
        pushStatus(client)
    # elif message.topic == TOPIC_ACTION_OFF and not proxy:
    #     action_off()
    # elif message.topic == TOPIC_ACTION_ON and not proxy:
    #     action_on()
    else:
        print("Topic unknown: " + message.topic)


def on_connect(client, userdata, flags, rc):
    print("Connected and powered on.")
    if PROXY:
        client.subscribe(TOPIC_STATUS_CLIENT)

    client.subscribe(TOPIC_ACTION_ON)

    pushStatus(client)
    client.subscribe(TOPIC_STATUS)
    client.on_message = receiveMessage


def on_disconnect(client, userdata, rc):
    print("Disconnect, reason: " + str(rc))
    print("Disconnect, reason: " + str(client))


def start():
    client = mqtt.Client(MQTT_CLIENT_NAME)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    print("about to connect on: " + BROKER)
    client.connect(BROKER, PORT)
    client.loop_forever()


if __name__ == "__main__":
    print("Starting mqtt client " + MQTT_CLIENT_NAME)
    start()
