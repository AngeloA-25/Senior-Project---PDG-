import socket
import threading

import kivy
from kivy import app
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
import sbcwireless
import jsonPDGParse

DEFAULT_WIDTH = 40
DEFAULT_HEIGHT = 40
GUI = 0

def receivefrommain(datachunk):
    print(datachunk)

def receivefromparse(connections, pending_devices = None):
#connections: (socket, parsed handshake) to show immediately
#pending_devices: (host, port) still to connect while the gui is open
    PortableDataGloveApp(connections, pending_devices).run()

#def sendtomainroutine()

class DevicePanel(BoxLayout):
#One panel per ESP32: its own buttons, labels, socket and polling
    def __init__(self, device_name, handshake, socketname, disconnect_callback = None, **kwargs):
        try:
            guiscale = max(1, int(handshake["SizeofGUI"]))
        except (TypeError, ValueError):
            guiscale = 1
        super().__init__(
            orientation = 'vertical',
            padding = 10 * guiscale,
            spacing = 10 * guiscale,
            **kwargs
        )
        self.device_name = device_name
        self.socketname = socketname
        self.disconnect_callback = disconnect_callback
        self.data_labels = []

        self.add_widget(Label(
            text = f"{device_name} - {handshake['Title']}",
            font_size = f'{16 * guiscale}sp',
        ))
        for name, value in handshake["Options"]:
            if name.startswith("Button"):
                button = Button(
                    text = value,
                    font_size = f'{14 * guiscale}sp',
                )
                button.bind(on_press = self.on_option_press)
                self.add_widget(button)
            else:
                label = Label(
                    text = f"{name}: {value}",
                    font_size = f'{14 * guiscale}sp',
                )
                self.data_labels.append((name, label))
                self.add_widget(label)

        disconnect = Button(
            text = "Disconnect",
            font_size = f'{14 * guiscale}sp',
            size_hint_y = None,
            height = 40 * guiscale,
        )
        disconnect.bind(on_press = self.on_disconnect_press)
        self.add_widget(disconnect)

    def on_option_press(self, button):
        sbcwireless.send_button(self.socketname, button.text)
        print(f"{self.device_name}: button pressed {button.text}")

    def on_disconnect_press(self, button):
        print(f"{self.device_name}: disconnect requested")
        if self.disconnect_callback is not None:
            self.disconnect_callback(self)

    def update_from_packet(self, packet):
        parsed = jsonPDGParse.parse_data(packet)
        if parsed["Type"] == "Float":
            for (name, label), value in zip(self.data_labels, parsed["Float"]):
                label.text = f"{name}: {value}"
        elif parsed["Type"] == "Word":
            print(f"{self.device_name}: word data {parsed['Word']}")
        elif parsed["Type"] == "Message":
            print(f"{self.device_name}: message {parsed['Message']}")


class PortableDataGloveApp(App):
    def __init__(self, connections, pending_devices = None, **kwargs):
        super().__init__(**kwargs)
        self.connections = connections
        self.pending_devices = pending_devices or []
        self.panels = []
        self.root_layout = None
        self.running = True

    def build(self):
        self.title = "Portable Data Glove"
        self.root_layout = BoxLayout(orientation = 'horizontal', padding = 10, spacing = 10)
        for socketname, handshake in self.connections:
            self.add_panel(socketname, handshake)
        return self.root_layout

    def add_panel(self, socketname, handshake):
        try:
            host, port = socketname.getpeername()[:2]
        except OSError:
            host, port = "unknown", 0
        panel = DevicePanel(f"{host}:{port}", handshake, socketname, self.remove_panel)
        self.panels.append(panel)
        self.root_layout.add_widget(panel)
        threading.Thread(target = self.poll_packets, args = (panel,), daemon = True).start()
        return panel

    def remove_panel(self, panel):
        if panel not in self.panels:
            return
        self.panels.remove(panel)
        self.root_layout.remove_widget(panel)
        try:
            panel.socketname.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            panel.socketname.close()
        except OSError:
            pass
        sbcwireless._recv_buffers.pop(panel.socketname, None)
        print(f"{panel.device_name}: disconnected, panel removed")

    def on_start(self):
        if self.pending_devices:
            threading.Thread(target = self.connect_pending, daemon = True).start()

    def connect_pending(self):
        for host, port in self.pending_devices:
            try:
                socketname, shake = sbcwireless.connect_device(host, port)
            except OSError as err:
                print(f"{host}:{port}: connection failed: {err}")
                continue
            handshake = jsonPDGParse.parse(shake)
            Clock.schedule_once(lambda dt, s = socketname, h = handshake: self.add_panel(s, h))

#Runs in a background thread per device, Clock brings the update back to the gui thread
    def poll_packets(self, panel):
        while self.running:
            try:
                packet = sbcwireless.recv_json(panel.socketname)
            except (OSError, ValueError) as err:
                if panel not in self.panels:
                    return
                print(f"{panel.device_name}: connection closed: {err}")
                Clock.schedule_once(lambda dt, panel = panel: self.remove_panel(panel))
                return
            Clock.schedule_once(lambda dt, p = packet, panel = panel: panel.update_from_packet(p))

    def on_stop(self):
        self.running = False
        for panel in self.panels:
            try:
                panel.socketname.close()
            except OSError:
                pass
