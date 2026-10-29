import kivy
from kivy import app
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
import sbcwireless
import jsonPDGParse
from kivy.uix.boxlayout import BoxLayout
import socket

DEFAULT_WIDTH = 40
DEFAULT_HEIGHT = 40
GUI = 0

def receivefromparse(options,senderID,message,dataparse1,dataparse2,dataparse3,dataparse4,floatval1,floatval2,floatval3,title,guiscale):
    print(options,senderID,message,dataparse1,dataparse2,dataparse3,dataparse4,floatval1,floatval2,floatval3,title,guiscale)
    PortableDataGloveApp(title, guiscale, options).run()

#def sendtomainroutine()

class PortableDataGloveApp(App):
    def __init__(self, window_title, guiscale, options, **kwargs):
        super().__init__(**kwargs)
        self.window_title = window_title
        try:
            self.gui_scale = max(1, int(guiscale))
        except (TypeError, ValueError):
            self.gui_scale = 1
        self.options = options

    def build(self):
        self.title = self.window_title
        layout = BoxLayout(
            orientation = 'vertical',
            padding = 10 * self.gui_scale,
            spacing = 10 * self.gui_scale,
        )
        layout.add_widget(Label(
            text = self.window_title,
            font_size = f'{18 * self.gui_scale}sp',
        ))
        for name, value in self.options:
            if name.startswith("Button"):
                button = Button(
                    text = value,
                    font_size = f'{14 * self.gui_scale}sp',
                )
                button.bind(on_press = self.on_option_press)
                layout.add_widget(button)
            else:
                layout.add_widget(Label(
                    text = f"{name}: {value}",
                    font_size = f'{14 * self.gui_scale}sp',
                ))
        return layout

    def on_option_press(self, button):
        print(f"button pressed: {button.text}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((sbcwireless.ESP32_WIFI_HOST, sbcwireless.ESP32_WIFI_PORT))
        data = button.text
        s.sendall(data)
