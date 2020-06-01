import paho.mqtt.client as mqtt

TOPIC_STATUS_CLIENT = "pc/status/client"
TOPIC_STATUS_PROXY = "pc/status/proxy"
TOPIC_STATUS = "pc/status"
PC_STATUS = "ON"
TOPIC_ACTION = "pc/action"

MQTT_CLIENT_NAME = "rpi3"
BROKER = "localhost"
PORT = 1883
PROXY = true


def receiveMessage(client, userdata, message):
    topic = str(message.topic)
    message = str(message.payload.decode("utf-8"))
    print("Received msg:", topic + " " + message)
    client.publish(TOPIC_STATUS, PC_STATUS)


def on_connect(client, userdata, flags, rc):
    print("Connected and powered on.")
    if PROXY:
        client.publish(TOPIC_STATUS_PROXY, "ON")
        client.subscribe(TOPIC_STATUS_CLIENT)
        # Attach the receiveMessage to subscription
    else:
        client.publish(TOPIC_STATUS_CLIENT, "ON")
    client.on_message = receiveMessage


def on_disconnect(client, userdata, rc):
    print("Disconnect, reason: " + str(rc))
    print("Disconnect, reason: " + str(client))


def start():
    client = mqtt.Client(MQTT_CLIENT_NAME)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    print("about to connect on: " + BROKER)
    client.connect(BROKER, 1883)
    client.loop_forever()


if __name__ == "__main__":
    print("Starting mqtt client " + MQTT_CLIENT_NAME)
    start()
