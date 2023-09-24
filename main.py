import flet as ft
import serial
import urllib.request
from configparser import ConfigParser
from time import sleep
from helpers import utils
import subprocess
import evdev

# version tag
__version__ = '0.1'


# importing config.ini file
config = ConfigParser()
config.read('config.ini')
# getting USB serial connection established
ser = serial.Serial(
    config.get('settings', 'COM'), baudrate=config.getint('settings', 'baud'), timeout=1, parity='N', stopbits=1,
)
# memory cache
cache = {'pushClicked': False, 'tag': '000000000'}

# sanatize read data from USB serial port to the application


def main(page: ft.Page):
    # status changer
    def status(value: str, reason: None = ''):
        if value == 'busy':
            status_icon.src = 'icons/yellow.png'
            status_value.value = 'PROCESSING'
        elif value == 'error':
            status_icon.src = 'icons/red.png'
            status_value.value = f'Error. {reason}'
        else:
            status_icon.src = 'icons/green.png'
            status_value.value = 'ready'
        page.update()

    # page preference
    page.window_full_screen = True
    page.fonts = {
        'Digital 7': 'https://www.1001fonts.com/download/font/digital-7.regular.ttf',
    }
    status_value = ft.Text(
        'READY',
        size=30,
        font_family='Digital 7',
    )
    status_icon = ft.Image(src='icons/green.png')
    weight_value = ft.Text(
        str(0),
        size=120,
        font_family='Digital 7',
    )
    customer_value = ft.Text(
        cache['tag'],
        size=120,
        font_family='Digital 7',
    )
    price_value = ft.Text(
        '0000.00',
        size=120,
        font_family='Digital 7',
    )
    date_value = ft.Text(
        '00-00-0000',
        size=120,
        font_family='Digital 7',
    )
    time_value = ft.Text(
        '00:00:00',
        size=120,
        font_family='Digital 7',
    )
    plate_value = ft.Text(
        'A0000',
        size=120,
        font_family='Digital 7',
    )
    final_weight_value = ft.Text(
        '0',
        size=120,
        font_family='Digital 7',
    )
    paid_value = ft.Text(
        'UNKNOWN',
        size=120,
        font_family='Digital 7',
    )
    page.appbar = ft.AppBar(
        leading=ft.Container(padding=5, content=status_icon),
        leading_width=40,
        title=status_value,
        bgcolor=ft.colors.BACKGROUND,
        actions=[
            ft.Container(
                padding=10, content=ft.Text(f'WAMCO WEIGHBRIDGE UNIT {__version__}', size=30, font_family='Digital 7'),
            ),
        ],
    )
    page.add(
        ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    'WEIGHT: ',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                weight_value,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    'ID: ',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                customer_value,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    'DATE: ',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                date_value,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    'TIME: ',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                time_value,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    'PRICE [MVR]: ',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                price_value,
                            ],
                        ),
                    ],
                ),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    'PLATE NO.: ',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                plate_value,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    'FINAL[KG]: ',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                final_weight_value,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    'PAID:',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                paid_value,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    '',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                # price_value,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    '',
                                    size=120,
                                    font_family='Digital 7',
                                ),
                                # price_value,
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )
    # a loop reading data coming from serial port
    for device in [evdev.InputDevice(fn) for fn in evdev.list_devices()]:
        if device.name == 'Sycreader USB Reader':
            device = evdev.InputDevice(device.path)
            container = []
            device.grab()
            for event in device.read_loop():
                data = ser.read_all()
                if data:
                    cache['data'] = utils.sanitize(data)
                    if cache['data'] != weight_value.value:
                        weight_value.value = utils.sanitize(data)
                if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    digit = evdev.ecodes.KEY[event.code]
                    if digit == 'KEY_ENTER':
                        status('busy')
                        tag = ''.join(i.strip('KEY_') for i in container)
                        customer_value.value = tag
                        date_value.value, time_value.value = utils.time_now()
                        container = []
                        page.update()
                        # HAHAHA CAUGHT IN 4K
                        try:
                            utils.camera_snapshot(
                                ip=config.get('settings', 'cam_ip'),
                                port=config.get('settings', 'cam_port'),
                                username=config.get(
                                    'settings', 'cam_username',
                                ),
                                password=config.get(
                                    'settings', 'cam_password',
                                ),
                                filename=customer_value.value,
                            )
                        except subprocess.CalledProcessError as e:
                            subprocess.run(
                                ['mkdir', 'snapshots'], check=False,
                            )
                            status(
                                'error', reason='Something went wrong, please try again',
                            )
                        # webhook implementation
                        urllib.request.urlopen(
                            urllib.request.Request(
                                config.get('settings', 'webhook').format(
                                    weight_value.value,
                                    customer_value.value,
                                    date_value.value,
                                    time_value.value,
                                ),
                                headers={'User-Agent': 'Mozilla/5.0'},
                            ),
                        ).read()

                        status('ready')
                        sleep(0.5)
                    else:
                        container.append(digit)


# RUN IT BACK
ft.app(main, assets_dir='assets', name='Weight Reader')
