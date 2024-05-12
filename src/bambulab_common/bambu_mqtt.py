from enum import Enum
from typing import TypedDict
import paho.mqtt.client as mqtt
import json
import ssl

from .printer import Printer


class mqttMode(Enum):
    """Contains mqtt mode"""

    LISTENER = "LISTENER"
    PUBLISHER = "PUBLISHER"


class mqttData(TypedDict):
    """Contains mqtt data"""

    mode: mqttMode
    printer: Printer


def create_client(printer: Printer) -> mqtt.Client:
    """Creates MQTT client"""
    client = mqtt.Client()
    client.username_pw_set("bblp", printer.printer_info["access"])
    client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
    client.on_connect = on_connect
    client.on_message = on_message
    return client


def client_thread_func(printer: Printer, mode: mqttMode, client: mqtt.Client):
    """function to feed to the thread"""
    data: mqttData = {"mode": mode, "printer": printer}
    client.user_data_set(data)
    client.connect(printer.printer_info["ip"], 8883, 60)
    client.loop_forever()


def on_connect(client: mqtt.Client, userdata: mqttData, flags, rc):
    """Callback for connection"""
    print("Connected with result code " + str(rc))
    if userdata["mode"] == mqttMode.LISTENER:
        client.subscribe(f"device/{userdata['printer'].printer_info['serial']}/report")


def on_message(client: mqtt.Client, userdata: mqttData, msg):
    """Callback function for when a message is received."""
    doc: dict = json.loads(msg.payload)

    if "print" in doc.keys():
        if "command" in doc["print"].keys() and "msg" in doc["print"].keys():
            if doc["print"]["command"] == "push_status":
                if doc["print"]["msg"] == 0:
                    handle_push_all(doc, userdata)
                elif doc["print"]["msg"] == 1:
                    handle_status_update(doc, userdata)
                else:
                    print("Unsupported push_status message. " + str(doc))
            else:
                print("Unsupported command. " + str(doc))
        else:
            print("Unsupported message, no cmd/msg. " + str(doc))

    else:
        print("Unsupported message, no print. " + str(doc))

    print(f"MESSAGE FROM {userdata['printer'].printer_info['id']}: ")
    print(json.dumps(doc))


def handle_push_all(doc, userdata):
    pass


def handle_status_update(doc, userdata):
    pass
