import flet as ft
import serial
import urllib.request
from configparser import ConfigParser
import contextlib
from time import sleep
import re
import evdev
import datetime

# version tag
__version__ = '0.1'


# importing config.ini file
config = ConfigParser()
config.read('config.ini')

# getting USB serial connection established
ser = serial.Serial(
    config.get('settings', 'COM'), baudrate=config.getint('settings', 'baud'), timeout=1, parity="N", stopbits=1
)
# memory cache
cache = {'pushClicked': False, 'tag': "000000000"}


# sanatize read data from USB serial port to the application
def sanitize(in_bin, result=""):
    with contextlib.suppress(IndexError):
        bb = in_bin.decode(encoding="ascii", errors="ignore")
        clean = re.findall(r"\d{8}", bb)
        return clean[0][:-2]


def main(page: ft.Page):
    #     urllib.request.urlopen(
    #         urllib.request.Request(
    #             f"https://n8n.cubable.date/webhook/weigh-bridge?weight={weight_value.value}",
    #             headers={'User-Agent': 'Mozilla/5.0'}
    #         )
    #     ).read()
    # status changer
    def status(value: str):
        if value == "busy":
            status_icon.src = "icons/yellow.png"
            status_value.value = "PROCESSING"
        elif value == "error":
            status_icon.src = "icons/red.png"
            status_value.value = "Error. restarting in 5 seconds"
        else:
            status_icon.src = "icons/green.png"
            status_value.value = "ready"
        page.update()

    # page preference
    page.window_full_screen = True
    page.fonts = {
        "Digital 7": "https://www.1001fonts.com/download/font/digital-7.regular.ttf"
    }
    status_value = ft.Text(
        "READY",
        size=30,
        font_family="Digital 7",
    )
    status_icon = ft.Image(src="icons/green.png")
    weight_value = ft.Text(
        str(0),
        size=100,
        font_family="Digital 7",
    )
    customer_value = ft.Text(
        cache['tag'],
        size=100,
        font_family="Digital 7",
    )
    price_value = ft.Text(
        "0000.00",
        size=100,
        font_family="Digital 7",
    )
    datetime_value = ft.Text(
        "00-00-0000 00:00",
        size=100,
        font_family="Digital 7",
    )
    page.appbar = ft.AppBar(
        leading=ft.Container(padding=5, content=status_icon),
        leading_width=40,
        title=status_value,
        bgcolor=ft.colors.BACKGROUND,
        actions=[
            ft.Container(
                padding=10, content=ft.Text(f"WAMCO WEIGHBRIDGE UNIT {__version__}", size=30, font_family="Digital 7")
            )
        ],
    )
    page.add(
        ft.Row(
                controls=[
                    ft.Text(
                        "WEIGHT: ",
                        size=100,
                        font_family="Digital 7",
                    ),
                    weight_value
                ]
        ),
        ft.Row(
                controls=[
                    ft.Text(
                        "CUSTOMER: ",
                        size=100,
                        font_family="Digital 7",
                    ),
                    customer_value
                ]
        ),
        ft.Row(
                controls=[
                    ft.Text(
                        "DATETIME: ",
                        size=100,
                        font_family="Digital 7",
                    ),
                    datetime_value
                ]
        ),
        ft.Row(
                controls=[
                    ft.Text(
                        "PRICE: ",
                        size=100,
                        font_family="Digital 7",
                    ),
                    price_value
                ]
        ),
    )
    # a loop reading data coming from serial port
    try:
        for device in [evdev.InputDevice(fn) for fn in evdev.list_devices()]:
            if device.name == "Sycreader USB Reader":
                device = evdev.InputDevice(device.path)
                container = []
                device.grab()
                for event in device.read_loop():
                    data = ser.read_all()
                    if data:
                        cache['data'] = sanitize(data)
                        if cache['data'] != weight_value.value:
                            weight_value.value = sanitize(data)
                    if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                        digit = evdev.ecodes.KEY[event.code]
                        if digit == 'KEY_ENTER':
                            status("busy")
                            # create and dump the tag
                            tag = "".join(i.strip('KEY_') for i in container)
                            customer_value.value = tag
                            current_datetime = datetime.datetime.now()
                            datetime_value.value = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
                            container = []
                            page.update()
                            sleep(0.7)
                        else:
                            container.append(digit)
                    status("ready")
    except KeyboardInterrupt:
        quit()
# RUN IT BACK
ft.app(main, assets_dir="assets", name="Weight Reader")