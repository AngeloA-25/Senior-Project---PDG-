import asyncio
import socket
import string
import sys
import json
import os
from functools import reduce
import operator
import datetime

ESP32_WIFI_HOST = ""
ESP32_WIFI_PORT = 5000
ESP32_BLE_MAC = ""
CONNECT_TIMEOUT = 5

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
def calculate_xor_checksum(data: str) -> int:
        return reduce(operator.xor, data.encode(), 0)

def passcode_attempt():
    pass_attempt = input("Enter Password for Device:")
    pass_message = {
        "Device_ID":    "PDG",
        "Checksum":     calculate_xor_checksum(pass_attempt),
        "Timestamp":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Addresser":    "",
        "Checksum2":    calculate_xor_checksum(pass_attempt),
        "Type":     "Message",
        "messages": {
            "Sender_ID":    local_ip,
            "Message":      pass_attempt,
        }
    }
    with open("password_attempt.json", "w",encoding="utf-8") as file:
        json.dump(pass_message, file, indent = 4)

def connect_wifi(host=ESP32_WIFI_HOST, port=ESP32_WIFI_PORT):




#
#def connect_bluetooth(mac=ESP32_BLE_MAC):
    #from bleak  import BleakScanner

#
#def start_server(host="0.0.0.0", port=ESP32_WIFI_PORT):

def main():
    passcode_attempt()

if __name__ == "__main__":
    main()
