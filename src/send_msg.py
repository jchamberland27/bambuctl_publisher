#!/usr/bin/python3
from bambulab_common.printer import Printer
from bambulab_common.bambu_mqtt import publish_mqtt_message
from wattbox import Wattbox, control_command


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


def send_wattbox_msg(
    target: str, command: str, printer_list: dict[str, Printer], wattbox: Wattbox
) -> tuple[str, int]:
    """Send a Wattbox control message"""
    if target == "all":
        status = 200
        for printer in printer_list:
            rc = wattbox.send_control_command(
                printer_list[printer].printer_info["outlet"], command
            )
            if rc != 200:
                status = rc
            if status == 200:
                return f"{command} OK", 200
            else:
                return f"{command} ERROR", status
    elif target not in printer_list.keys():
        return "PRINTER NOT FOUND", 404
    else:
        rc = wattbox.send_control_command(
            printer_list[target].printer_info["outlet"], command
        )
        if rc == 200:
            return f"{command} OK", 200
        else:
            return f"{command} ERROR", rc
    pass
