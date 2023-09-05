import flet as ft
import serial
import urllib.request
from configparser import ConfigParser
import contextlib
from time import sleep

__version__ = '0.1'

config = ConfigParser()
config.read('config.ini')

ser = serial.Serial(
        config.get('settings', 'COM'), baudrate=config.getint('settings', 'baud'), timeout=1,
    )
cache = {}
cache['pushClicked'] = False


def sanitize(data, result=""):
    for char in data:
        if char.isdigit():
            result += char
    if not result:
        result = "0"
    return str(result)


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
        if cache['pushClicked']:
            page.snack_bar.open = True
            page.update()
        cache['pushClicked'] = True
        urllib.request.urlopen(
            urllib.request.Request(
                f"https://n8n.cubable.date/webhook/weigh-bridge?weight={weight_view.value}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
        ).read()
    def copyClick(e):
        e.page.set_clipboard(weight_view.value)
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
        sleep(0.5)
        data = ser.readline().decode().strip()
        if data:
            cache["data"] = sanitize(data)

ft.app(main, assets_dir="assets", name="Weight Reader")