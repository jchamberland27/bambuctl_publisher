#!/usr/bin/python3

from typing import TypedDict
import requests
from requests.auth import HTTPBasicAuth
import xmltodict
import os

WATTBOX_COMMANDS = {
    "POWER_OFF": 0,
    "POWER_ON": 1,
    "POWER_CYCLE": 3,
    "AUTO_REBOOT_ON": 4,
    "AUTO_REBOOT_OFF": 5,
}


class Outlet(TypedDict):
    """Contains info for an individual outlet"""

    number: int
    name: str
    status: str
    mode: str


class WattboxInfo(TypedDict):
    """Type definition for WattboxInfo"""

    ip: str
    username: str
    password: str
    outlets: list[Outlet]
    hostname: str
    model: str
    sn: str


class Wattbox:
    """Class for tracking a Wattbox"""

    wattbox_info: WattboxInfo

    def __init__(self):
        """Initializes Wattbox object"""

        self.wattbox_info = WattboxInfo()
        self.wattbox_info["ip"] = os.getenv("WATTBOXIP")
        self.wattbox_info["username"] = os.getenv("WATTBOXUSER")
        self.wattbox_info["password"] = os.getenv("WATTBOXPASS")
        self.wattbox_info["outlets"] = []
        self.getInfo()

    def getInfo(self) -> list[Outlet]:
        """retireve outlets"""
        response = requests.get(
            f"http://{self.wattbox_info['ip']}/wattbox_info.xml",
            auth=HTTPBasicAuth(
                self.wattbox_info["username"], self.wattbox_info["password"]
            ),
            headers={"Connection": "keep-alive", "User-Agent": "APP"},
        )
        if response.status_code == 200:
            self.parse_info_xml(response.content)
        else:
            return []

    def parse_info_xml(self, xml: str):
        doc = xmltodict.parse(xml)
        self.wattbox_info["hostname"] = doc["request"]["host_name"]
        self.wattbox_info["model"] = doc["request"]["hardware_version"]
        self.wattbox_info["sn"] = doc["request"]["serial_number"]

        outlet_names = doc["request"]["outlet_name"].split(",")
        outlet_satuses = doc["request"]["outlet_status"].split(",")
        outlet_modes = doc["request"]["outlet_method"].split(",")

        for i in range(len(outlet_names)):
            self.wattbox_info["outlets"].append(
                {
                    "number": i,
                    "name": outlet_names[i],
                    "status": translate_status(outlet_satuses[i]),
                    "mode": translate_mode(outlet_modes[i]),
                }
            )

    def send_control_command(self, outlet: str, command: str) -> int:
        """Send a control command to a Wattbox outlet"""
        if command not in WATTBOX_COMMANDS.keys():
            return 400
        response = requests.get(
            f"http://{self.wattbox_info['ip']}/control.cgi?outlet={outlet}&command={WATTBOX_COMMANDS[command]}",
            auth=HTTPBasicAuth(
                self.wattbox_info["username"], self.wattbox_info["password"]
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
