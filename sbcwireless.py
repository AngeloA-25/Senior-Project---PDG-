import asyncio
import socket
import string
import sys
import json
import os
from functools import reduce
import operator
import datetime
import time
import jsonPDGParse
import threading
import guitest
import asyncio
from bleak import BleakScanner

HOST = '0.0.0.0'
PORT = 55555
ESP32_WIFI_HOST = "127.0.0.1"  # TEST value - swap back to the real ESP32 IP later
ESP32_WIFI_HOST2 = "127.0.0.1"
ESP32_WIFI_PORT = 5000
ESP32_WIFI_PORT2 = 5001
#ESP32_BLE_MAC = ""
#ESP32_CHARACTERISTICS_UUID = ""
CONNECT_TIMEOUT = 5

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
def calculate_xor_checksum(data: str) -> int:
        return reduce(operator.xor, data.encode(), 0)

_recv_buffers = {}

def recv_json(socketname):
    buffer = _recv_buffers.get(socketname, b"")
    while b"\n" not in buffer:
        chunk = socketname.recv(1024)
        if not chunk:
            raise ConnectionResetError("connection closed before full packet")
        buffer += chunk
    line, rest = buffer.split(b"\n", 1)
    _recv_buffers[socketname] = rest
    return json.loads(line.decode())

def passcode_attempt(socketname):
    pass_attempt = input("Enter Password for Device:")
    pass_message = {
        "Device_ID":    "PDG",
        "Checksum":     calculate_xor_checksum(pass_attempt),
        "Timestamp":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Addresser":    "",
        "Checksum_2":    calculate_xor_checksum(pass_attempt),
        "Type":     "Message",
        "messages": {
            "Sender_ID":    local_ip,
            "Message":      pass_attempt,
        }
    }
    with open("password_attempt.json", "w",encoding="utf-8") as file:
        json.dump(pass_message, file, indent = 4)
    try:
        socketname.sendall(json.dumps(pass_message).encode() + b"\n")
    except (BrokenPipeError, ConnectionResetError):
        print("Connection lost while sending password")

#def remember_device()://After device has been connected store a memory of device name/ip


#def multi():// unsure if needed


#def scan()://Also on gui button press, in titlebar


#Should be multithreaded to allow for multiple devices to connect - To Do
def connect_wifi(host = ESP32_WIFI_HOST, port = ESP32_WIFI_PORT):
    os.system('clear')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    passcode_attempt(s)
    data = recv_json(s)
    deviceID = data['Device_ID']
    checksum1 = data['Checksum']
    timestamp = data['Timestamp']
    address = data['Addresser']
    checksum2 = data['Checksum_2']
    dataType = data['Type']
    if checksum2 != checksum1:
        print("Data May Be Corrupted Try Again")
        connect_wifi(host,port)
    if dataType == "Message":
        messagedata = list(data['messages'].values())
        senderID = messagedata[0]
        message = messagedata[1]
        if message == "Accepted":
            shake = recv_json(s)
            jsonPDGParse.parse(shake)
        if message == "Incorrect Password":
            print("Incorrect Password Please Try Again")
            time.sleep(2)
            os.system('clear')
            s.close()
            connect_wifi(host , port)

#-- Bluetooth version of the connection Also multithreaded if bluetooth allows
#async def connect_bluetooth():
    #devices = await BleakScanner.discover()


#def ping():

def main():
    connect_wifi()
if __name__ == "__main__":
    main()
