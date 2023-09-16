import flet as ft
import serial
import urllib.request
from configparser import ConfigParser
import contextlib
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
    # push button function
    def pushClick(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Data already pushed!"),
            action="Ok",
        )
        if cache['pushClicked'] or weight_view.value == "0":
            page.snack_bar.open = True
            return page.update()
        cache['pushClicked'] = True
        # urllib.request.urlopen(
        #     urllib.request.Request(
        #         f"https://n8n.cubable.date/webhook/weigh-bridge?weight={weight_view.value}",
        #         headers={'User-Agent': 'Mozilla/5.0'}
        #     )
        # ).read()
    # copy button function
    def copyClick(e):
        e.page.set_clipboard(weight_view.value)
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"`{weight_view.value}`copied"),
            action="Ok",
        )
        page.snack_bar.open = True
        return page.update()
    # all buttons on page
    def Buttons():
        return [
            ft.Container(
                content=ft.ElevatedButton("Push", on_click=pushClick)
            ),
            ft.Container(
                content=ft.ElevatedButton("Copy", on_click=copyClick)
            ),
        ]

    # page preference
    page.window_width = 300
    page.window_height = 200
    page.window_resizable = False
    page.fonts = {
        "Digital 7": "https://www.1001fonts.com/download/font/digital-7.regular.ttf"
    }
    weight_view = ft.Text(
        str(0),
        size=50,
        weight=ft.FontWeight.W_700,
        selectable=True,
        font_family="Digital 7"
    )
    page.add(
        ft.Container(
            content=ft.Row(Buttons()),
        ),
        weight_view,
    )
    # a loop reading data coming from serial port
    while True:
        data = ser.read_all()
        if data:
            sleep(0.5)
            cache['data'] = sanitize(data)
            if cache['data'] != weight_view.value:
                weight_view.value = sanitize(data)
                page.update()

# RUN IT BACK
ft.app(main, assets_dir="assets", name="Weight Reader")