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
ESP32_WIFI_HOST = "10.39.42.173"  # TEST value - swap back to the real ESP32 IP later
ESP32_WIFI_HOST2 = "127.0.0.1"
ESP32_WIFI_PORT = 5000
ESP32_WIFI_PORT2 = 5001
#ESP32_BLE_MAC = ""
#ESP32_CHARACTERISTICS_UUID = ""
CONNECT_TIMEOUT = 50

DEVICES = [
    (ESP32_WIFI_HOST, ESP32_WIFI_PORT),
    (ESP32_WIFI_HOST2, ESP32_WIFI_PORT2),
]

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
def calculate_xor_checksum(data: str) -> int:
        return reduce(operator.xor, data.encode(), 0)

_recv_buffers = {}

def recv_json(socketname, debug=False):
    buffer = _recv_buffers.get(socketname, b"")
    while b"\n" not in buffer:
        try:
            chunk = socketname.recv(1024)
        except TimeoutError:
            if buffer and debug:
                print(f"Received {len(buffer)} byte(s) but no newline yet: {buffer[-200:]!r}")
                _recv_buffers[socketname] = buffer
            raise
        if not chunk:
            raise ConnectionResetError("connection closed before full packet")
        buffer += chunk
    line, rest = buffer.split(b"\n", 1)
    _recv_buffers[socketname] = rest
    if debug:
        print(f"Received line ({len(line)} bytes): {line[:500]!r}")
    return json.loads(line.decode())

def send_json(socketname, packet):
    socketname.sendall(json.dumps(packet).encode() + b"\n")

def send_button(socketname, value):
    socketname.sendall(value.encode('utf-8') + b"\n")

def passcode_attempt(socketname, devicename="Device"):
    pass_attempt = input(f"Enter Password for Device {devicename}:")
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

#def remember_device():
#
#def wifi_scan()://Toolbar
#
async def ble_scan():
    bledev = BleakScanner.discover()


def connect_device(host, port):
    devicename = f"{host}:{port}"
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(CONNECT_TIMEOUT)
        passcode_attempt(s, devicename)
        print(f"{devicename}: password sent, waiting up to {CONNECT_TIMEOUT}s for reply...")
        try:
            data = recv_json(s, debug=True)
        except (TimeoutError, ConnectionResetError) as err:
            print(f"{devicename}: no usable response after password attempt ({err}), retrying")
            s.close()
            time.sleep(2)
            continue
        except (ValueError, UnicodeDecodeError) as err:
            print(f"{devicename}: reply was not valid JSON ({err}), retrying")
            s.close()
            time.sleep(2)
            continue
        print(f"{devicename}: reply parsed as {data}")
        if data.get('Type') == "Message":
            message = list(data.get('messages', {}).values())[1]
            if message in ("Access Granted", "Accepted"):
                print("Correct")
                try:
                    shake = recv_json(s, debug=True)
                except (TimeoutError, ConnectionResetError) as err:
                    print(f"{devicename}: no handshake received ({err}), retrying")
                    s.close()
                    time.sleep(2)
                    continue
                except (ValueError, UnicodeDecodeError) as err:
                    print(f"{devicename}: handshake was not valid JSON ({err}), retrying")
                    s.close()
                    time.sleep(2)
                    continue
                print(shake)
                s.settimeout(None)
                return s, shake
            print(f"{devicename}: password rejected ({message!r}) Please Try Again")
        else:
            print(f"{devicename}: unexpected reply Type {data.get('Type')!r} Please Try Again")
        s.close()
        time.sleep(2)

def connect_wifi():
    os.system('clear')
    host, port = DEVICES[0]
    s, shake = connect_device(host, port)
    guitest.receivefromparse([(s, jsonPDGParse.parse(shake))], DEVICES[1:])

#-- Bluetooth version of the connection Also multithreaded if bluetooth allows
#async def connect_bluetooth():



#def ping():

def main():
    connect_wifi()
if __name__ == "__main__":
    main()
