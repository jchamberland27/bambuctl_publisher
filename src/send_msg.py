#!/usr/bin/python3
from bambulab_common.printer import Printer
from bambulab_common.bambu_mqtt import publish_mqtt_message


def send_mqtt_msg(
    target: str, command: str, printer_list: dict[str, Printer]
) -> tuple[str, int]:
    """Send an MQTT message to a printer"""
    if target == "all":
        for printer in printer_list:
            publish_mqtt_message(printer_list[printer], command)
            return "OK", 200
    elif target not in printer_list.keys():
        return "PRINTER NOT FOUND", 404
    else:
        publish_mqtt_message(printer_list[target], command)
        return "OK", 200
