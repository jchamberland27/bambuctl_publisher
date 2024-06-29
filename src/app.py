from dotenv import load_dotenv
from flask import Flask, request
from typing import Dict
from threading import Thread
from redis import Redis
from bambulab_common.printer import Printer
import bambulab_common.bambu_mqtt as bambu_mqtt
import bambulab_common.commands as commands
from send_msg import send_mqtt_msg, send_wattbox_msg, send_lftp_clean_thread
from wattbox import Wattbox
import os

app = Flask(__name__)
printer_list: dict[str, Printer] = {}
wattbox: Wattbox = None


@app.route("/status")
def status():
    """Health check endpoint"""
    return "OK", 200


@app.route("/printers/list")
def list_printers():
    """List all printers"""
    return {
        "printers": [printer_list[printer].printer_info for printer in printer_list]
    }, 200


@app.route("/wattbox/list")
def list_wattbox():
    """List all wattbox info"""
    return wattbox.wattbox_info, 200


@app.route("/<target>/clean")
def clean(target: str):
    """Clean a printer"""
    return send_lftp_clean_thread(target, printer_list)


@app.route("/<target>/lights/on")
def lights_on(target: str):
    """Turn on the lights on a printer"""
    return send_mqtt_msg(target, commands.CHAMBER_LIGHT_ON, printer_list)


@app.route("/<target>/lights/off")
def lights_off(target: str):
    """Turn off the lights on a printer"""
    return send_mqtt_msg(target, commands.CHAMBER_LIGHT_OFF, printer_list)


@app.route("/<target>/print/pause")
def print_pause(target: str):
    """Pause a printer"""
    return send_mqtt_msg(target, commands.PAUSE, printer_list)


@app.route("/<target>/power/on")
def power_on(target: str):
    """Power on a printer via Wattbox"""
    return send_wattbox_msg(target, "POWER_ON", printer_list, wattbox)


@app.route("/<target>/power/off")
def power_off(target: str):
    """Power on a printer via Wattbox"""
    return send_wattbox_msg(target, "POWER_OFF", printer_list, wattbox)


@app.route("/<target>/power/cycle")
def power_cycle(target: str):
    """Power on a printer via Wattbox"""
    return send_wattbox_msg(target, "POWER_CYCLE", printer_list, wattbox)


@app.route("/<target>/print/resume")
def print_resume(target: str):
    """Resume a printer"""
    return send_mqtt_msg(target, commands.RESUME, printer_list)


@app.route("/<target>/print/stop")
def print_stop(target: str):
    """Stop a printer"""
    return send_mqtt_msg(target, commands.STOP, printer_list)


def build_printer_list(printers, db: Redis) -> Dict[str, Printer]:
    """Build and load a Printer object for each printer"""
    printer_dict: Dict[str, Printer] = {}
    for printer_id in printers:
        printer = Printer(printer_id, db)
        client = bambu_mqtt.create_client(printer)
        printer.set_client(client)
        printer_dict[printer_id] = printer
    return printer_dict


def main():
    """Main function"""
    global printer_list
    global wattbox
    load_dotenv()

    print("Setting up Redis and retrieving printers...")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    db = Redis(host=redis_host, port=redis_port, decode_responses=True)
    printers = db.lrange("printer_ids", 0, -1)

    print("Building printer list...")
    printer_list = build_printer_list(printers, db)

    print("Setting up Wattbox...")
    wattbox = Wattbox()

    app.run(host="0.0.0.0", port=51295)


if __name__ == "__main__":
    main()
