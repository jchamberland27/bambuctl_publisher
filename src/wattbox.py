#!/usr/bin/python3

import json
import os
from typing import TypedDict

from redis import Redis
import requests
from requests.auth import HTTPBasicAuth
import xmltodict


WATTBOX_COMMANDS = {
    "POWER_OFF": 0,
    "POWER_ON": 1,
    "POWER_CYCLE": 3,
    "AUTO_REBOOT_ON": 4,
    "AUTO_REBOOT_OFF": 5,
}


class Outlet(TypedDict):
    """Contains info for an individual outlet"""

    name: str
    ip: str
    number: int
    username: str
    password: str
    status: str
    mode: str
    hostname: str
    model: str
    sn: str


class Wattbox:
    """Class for maintaining the list of outlets"""

    outlets: dict[Outlet]

    def __init__(self):
        """Initializes Wattbox object"""

        self.outlets = {}
        wr = Redis(
            os.getenv("WATTBOX_REDIS_IP"),
            os.getenv("WATTBOX_REDIS_PORT"),
            decode_responses=True,
        )
        keys = wr.keys()
        # data = wr.get(key) for key in keys}
        for key in keys:
            data = json.loads(wr.get(key))
            new_outlet: Outlet = {
                "name": data["name"],
                "ip": data["ip"],
                "number": int(data["number"]),
                "username": data["username"],
                "password": data["password"],
                "status": "TBD",
                "mode": "TBD",
                "hostname": "TBD",
                "model": "TBD",
                "sn": "TBD",
            }
            print(new_outlet)
            response = requests.get(
                f"http://{new_outlet['ip']}/wattbox_info.xml",
                auth=HTTPBasicAuth(new_outlet["username"], new_outlet["password"]),
                headers={"Connection": "keep-alive", "User-Agent": "APP"},
            )
            if response.status_code == 200:
                xml_data = xmltodict.parse(response.content)
                new_outlet["hostname"] = xml_data["request"]["host_name"]
                new_outlet["model"] = xml_data["request"]["hardware_version"]
                new_outlet["sn"] = xml_data["request"]["serial_number"]

                outlet_names = xml_data["request"]["outlet_name"].split(",")
                outlet_satuses = xml_data["request"]["outlet_status"].split(",")
                outlet_modes = xml_data["request"]["outlet_method"].split(",")

                new_outlet["status"] = translate_status(
                    outlet_satuses[new_outlet["number"] - 1]
                )
                new_outlet["mode"] = translate_mode(
                    outlet_modes[new_outlet["number"] - 1]
                )
                self.outlets[key] = new_outlet

    def dump(self) -> dict:
        """Dump Wattbox info"""
        return self.outlets

    def send_control_command(self, outlet: str, command: str) -> int:
        """Send a control command to a Wattbox outlet"""
        if command not in WATTBOX_COMMANDS.keys():
            return 400
        elif outlet not in self.outlets.keys():
            return 404
        response = requests.get(
            f"http://{self.outlets[outlet]['ip']}/control.cgi?outlet={str(self.outlets[outlet]['number'])}&command={WATTBOX_COMMANDS[command]}",
            auth=HTTPBasicAuth(
                self.outlets[outlet]["username"], self.outlets[outlet]["password"]
            ),
            headers={"Connection": "keep-alive", "User-Agent": "APP"},
        )
        return response.status_code


def translate_status(status: str) -> str:
    """Translate status from number to string"""
    if status == "0":
        return "OFF"
    if status == "1":
        return "ON"
    return "UNKNOWN"


def translate_mode(mode: str) -> str:
    """Translate mode from number to string"""
    if mode == "1":
        return "NORMAL"
    if mode == "2":
        return "RESET_ONLY"
    return "UNKNOWN"
