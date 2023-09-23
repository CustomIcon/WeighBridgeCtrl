import flet as ft
import serial
import urllib.request
from configparser import ConfigParser
import contextlib
import sys
from time import sleep
import re

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
cache = {'pushClicked': False}

# sanatize read data from USB serial port to the application
def sanitize(in_bin, result=""):
    with contextlib.suppress(IndexError):
        bb = in_bin.decode(encoding="ascii", errors="ignore")
        clean = re.findall(r"\d{8}", bb)
        return clean[0][:-2]


# main page
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
        "",
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
    )
    # a loop reading data coming from serial port
    while True:
        data = ser.read_all()
        if data:
            sleep(0.5)
            cache['data'] = sanitize(data)
            if cache['data'] != weight_value.value:
                weight_value.value = sanitize(data)
                page.update()
        for line in sys.stdin:
            customer_value.value = line.strip()
            page.update()

# RUN IT BACK
ft.app(main, assets_dir="assets", name="Weight Reader")