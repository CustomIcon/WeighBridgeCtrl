import flet as ft
import serial
import urllib.request
from configparser import ConfigParser
import contextlib
from time import sleep
import re

__version__ = '0.1'

config = ConfigParser()
config.read('config.ini')

ser = serial.Serial(
        config.get('settings', 'COM'), baudrate=config.getint('settings', 'baud'), timeout=1, parity="N", stopbits=1
    )
cache = {'pushClicked': False}


def sanitize(in_bin, result=""):
    with contextlib.suppress(IndexError):
        bb = in_bin.decode(encoding="ascii", errors="ignore")
        clean = re.findall(r"\d{8}", bb)
        return clean[0][:-2]


def main(page: ft.Page):
    def readClick(e):
        with contextlib.suppress(KeyError):
            weight_view.value = cache["data"]
        cache['pushClicked'] = False
        page.update()
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
        with open("Z:\WeighBridgeTest\weight.txt", "w") as f:
            f.write(weight_view.value)
    def copyClick(e):
        e.page.set_clipboard(weight_view.value)
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"`{weight_view.value}`copied"),
            action="Ok",
        )
        page.snack_bar.open = True
        return page.update()
    def Buttons():
        return [
            ft.Container(
                content=ft.ElevatedButton("Read", on_click=readClick)
            ),
            ft.Container(
                content=ft.ElevatedButton("Push", on_click=pushClick)
            ),
            ft.Container(
                content=ft.ElevatedButton("Copy", on_click=copyClick)
            ),
        ]

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
    while True:
        # sleep(0.5)
        data = ser.read_all()
        if data:
            sleep(0.5)
            cache["data"] = sanitize(data)
            weight_view.value = cache["data"]
            page.update()

ft.app(main, assets_dir="assets", name="Weight Reader")