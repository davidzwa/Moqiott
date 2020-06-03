import paho.mqtt.client as mqtt
import time
import atexit
from enum import IntEnum

BROKER = "10.0.4.35"
PORT = 1883

STATUS_QUERY = "status/query"
STATUS_CLIENT_QUERY = "status/client/query"  # Query specific
STATUS_CLIENT_RESPONSE = "status/client/response"  # Response specific
POWER_TOGGLE_DIRECT = "power/toggle-direct"

MQTT_CLIENT_NAME = "pc-mqtt-docker"


class ClientState(IntEnum):
    unknown = 1
    powering_on = 2
    on = 3
    powering_off = 4
    off = 5
    timeout = 6


def pushStatus(client):
    client.publish(STATUS_CLIENT_RESPONSE, int(ClientState.on))


def receiveMessage(client, userdata, message):
    topic = message.topic
    message = str(message.payload.decode("utf-8"))
    print("Received msg:", topic + " " + message)
    if topic == STATUS_CLIENT_QUERY or topic == STATUS_QUERY:
        pushStatus(client)
    elif topic == POWER_TOGGLE_DIRECT:
        pass
    else:
        print("Topic unknown: " + topic)


def on_connect(client, userdata, flags, rc):
    print("PC Connected and powered on.")
    client.subscribe(STATUS_CLIENT_QUERY)
    client.subscribe(STATUS_QUERY)
    client.subscribe(POWER_TOGGLE_DIRECT)

    pushStatus(client)
    client.on_message = receiveMessage


def on_disconnect(client, userdata, rc):
    print("Disconnect, reason: " + str(rc))
    print("Disconnect, reason: " + str(client))


def start(client: mqtt.Client):
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    print("about to connect on: " + BROKER)
    client.connect(BROKER, PORT)
    client.loop_forever()


def send_shutdown(client: mqtt.Client):
    print("Service ending. Announcing shuting-down state. " + MQTT_CLIENT_NAME)
    client.publish(STATUS_CLIENT_RESPONSE, ClientState.powering_off)


if __name__ == "__main__":
    print("Starting mqtt client " + MQTT_CLIENT_NAME)
    client = mqtt.Client(MQTT_CLIENT_NAME)

    # Starting daemon
    atexit.register(send_shutdown, client)
    start(client)
