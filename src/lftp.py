#!/usr/bin/python3


import subprocess
from threading import Thread

from bambulab_common.printer import Printer


def run_lftp_script(
    host: str, port: str, username: str, password: str, script: str
) -> tuple[bool, str]:
    """Run an LFTP script"""
    try:
        path = f"lftp/./{script}.sh"
        result: subprocess.CompletedProcess = subprocess.run(
            [path, host, port, username, password], capture_output=True, text=True
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


def cleaning_thread_func(printers: dict[str, Printer]):
    """Run LFTP cleanup scripts"""
    for printer in printers:
        run_lftp_script(
            printers[printer].printer_info["ip"],
            "990",
            "bblp",
            printers[printer].printer_info["access"],
            "clean_gcode",
        )
        run_lftp_script(
            printers[printer].printer_info["ip"],
            "990",
            "bblp",
            printers[printer].printer_info["access"],
            "clean_cam",
        )
        run_lftp_script(
            printers[printer].printer_info["ip"],
            "990",
            "bblp",
            printers[printer].printer_info["access"],
            "clean_log",
        )
        run_lftp_script(
            printers[printer].printer_info["ip"],
            "990",
            "bblp",
            printers[printer].printer_info["access"],
            "clean_recorder",
        )


def run_lftp_clean_thread(printers: dict[str, Printer]):
    """Run LFTP script on one or more printers"""
    Thread(target=cleaning_thread_func, args=(printers,)).start()
