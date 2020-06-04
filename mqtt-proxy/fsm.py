import paho.mqtt.client as mqtt
from printy import printy
from enum import IntEnum
import traceback

import powertoggle
import utils
import app_logging

logger = app_logging.get_logger()

STATUS_QUERY = "status/query"  # Query all statuses
STATUS_CLIENT = "status/client"
STATUS_CLIENT_QUERY = "status/client/query"  # Query specific
STATUS_CLIENT_RESPONSE = "status/client/response"  # Response specific
STATUS_PROXY = "status/proxy"

POWER_QUERY = "power/query"
POWER_RESPONSE = "power/response"
POWER_TOGGLE = "power/toggle"

TIMEOUT_QUICK = 500
TIMEOUT_POWEROFF = 2500
TIMEOUT_LONG = 5000


class ClientState(IntEnum):
    unknown = 1
    powering_on = 2
    on = 3
    powering_off = 4
    off = 5
    timeout = 6


class State(IntEnum):
    booting = 1
    await_mqtt = 2
    connected = 3
    querying = 4
    shutting_down = 5
    await_response = 6  # U expect a short timeout to be fine
    # U have no clue (unknown, powering_on, timeout): long timeout this time
    await_timeout = 7
    await_power = 8  # U are pretty sure it is powering off, semi-long timeout


class FsmActor(object):
    def __init__(self, client: mqtt.Client):
        self.current_power = ClientState.unknown
        self.state = State.booting
        self.reference_time_ms = utils.get_millis()

        self.client = client
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.log_message

    def start_connection(self, broker, port):
        if self.state == State.booting:
            self.client.connect(broker, port)
            if not self.client.is_connected:
                self.__set_awaiting()
        else:
            logger.warning(
                "Cant start FsmActor as it has already been started.")

    def subscribe_topics(self):
        self.client.subscribe(POWER_QUERY)
        self.client.subscribe(STATUS_QUERY)
        self.client.subscribe(STATUS_CLIENT_RESPONSE)
        self.client.subscribe(POWER_TOGGLE)

    def on_message(self, client: mqtt.Client, userdata, message):
        try:
            topic = message.topic
            message = str(message.payload.decode("utf-8"))
            logger.info(
                "Received topic: '{}', msg: '{}'".format(topic, message))
            if topic == STATUS_QUERY:
                logger.info("Processing status query")
                self.__send_state()
            elif topic == POWER_QUERY:
                logger.info("Starting proxied power query")
                self.__set_querying()
            elif topic == STATUS_CLIENT_RESPONSE:
                self.current_power = ClientState.on
                self.__set_connected()
            elif topic == POWER_TOGGLE:
                if self.current_power is ClientState.unknown:
                    # We gotta query first
                    self.__set_querying()
                    return

                if self.current_power is ClientState.on:
                    self.current_power = ClientState.powering_off
                elif self.current_power is ClientState.powering_off or self.current_power is ClientState.powering_on:
                    # Dont undertake action when powering off/on
                    # self.__send_power()
                    return
                else:
                    self.current_power = ClientState.powering_on

                powertoggle.action_toggle()
                self.__send_power()
                logger.info("Power action. ClientState: " +
                            str(self.current_power))
        except Exception as e:
            traceback.print_exc()
            logger.error("Handle message exception {}".format(str(e)))

    def send_refresh(self):
        self.__send_state()
        self.__send_power()

    def trigger_query(self):
        self.__set_querying()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        if self.state == State.await_mqtt:
            printy("✓ Connected and powered on.", "n")
        else:
            logger.warning("Reconnected on mqtt.")
        self.__set_connected()
        self.subscribe_topics()

    def on_disconnect(self, client: mqtt.Client, userdata, rc):
        self.__set_awaiting()
        logger.warning("✗ Disconnect, reason: " + str(rc), "r")
        client.loop_stop()

    def dispose(self):
        self.__set_shutdown()

    def log_message(self, client: mqtt.Client, msg: str):
        logger.info(msg)

    def __set_awaiting(self):
        self.state = State.await_mqtt
        pass  # Cant update with status message

    def __set_connected(self):
        self.state = State.connected
        self.__send_state()

    def __set_querying(self):
        if self.state == State.querying:
            logger.warning(
                "Already querying. Skipping request as it is rate limited.")
            return
        elif self.state == State.booting or self.state == State.await_mqtt:
            logger.warning("Still awaiting connection. Cant query.")
            return
        elif self.state == State.await_power or self.state == State.await_timeout or self.state == State.await_response:
            # We are still in waiting state...
            if self.__check_timeout_exceeded():
                self.current_power = ClientState.timeout
                logger.warning("Not Querying client, timeout exceeded.")
                self.__send_power()
            else:
                logger.warning(
                    "Not Querying client as a timeout is still running.")
            return

        self.state = State.querying
        self.__send_client_query()
        logger.warning("Querying client.")
        self.__set_process_timeout_type()
        pass
        # ClientState.unknown or self.current_power == ClientState.off or self.current_power == ClientState.powering_off:

    def __set_process_timeout_type(self):
        # (unknown, powering_on, timeout)
        if self.current_power == ClientState.unknown \
                or self.current_power == ClientState.powering_on \
                or self.current_power == ClientState.off \
                or self.current_power == ClientState.timeout:
            self.reference_time_ms = utils.get_millis()
            self.__set_await_timeout()
        elif self.current_power == ClientState.powering_off:
            self.__set_poweroff_timeout()
        elif self.current_power == ClientState.on:
            self.__set_response_timeout()

    def get_timeout_time(self):
        timeout = 0
        if self.state == State.await_power:
            timeout = TIMEOUT_POWEROFF
        elif self.state == State.await_response:
            timeout = TIMEOUT_QUICK
        elif self.state == State.await_timeout:
            timeout = TIMEOUT_LONG
        else:
            return (0, None)

        reference2_time_ms = utils.get_millis()
        if self.reference_time_ms is None:
            self.reference_time_ms = reference2_time_ms
        diff = reference2_time_ms - self.reference_time_ms
        return (diff, timeout)

    def __set_response_timeout(self):
        self.state = State.await_response

    def __set_poweroff_timeout(self):
        self.state = State.await_power

    def __set_await_timeout(self):
        self.state = State.await_timeout
        # External factors can trigger us now

    def __set_shutdown(self):
        self.state = State.shutting_down
        self.__send_state()

    def __check_timeout_exceeded(self) -> bool:
        diff, timeout = self.get_timeout_time()
        return diff > timeout

    def __send_client_query(self):
        self.client.publish(STATUS_CLIENT_QUERY)
        logger.info("Sent client query.")

    def __send_state(self):
        self.client.publish(STATUS_PROXY, int(self.state))
        logger.info("Sent state: {} ({})".format(
            str(self.state), int(self.state)))

    def __send_power(self):
        self.client.publish(
            POWER_RESPONSE, int(self.current_power))
        logger.info("Sent power message: {} ({})".format(
            str(self.current_power), int(self.state)))
