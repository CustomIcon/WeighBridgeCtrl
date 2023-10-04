import flet as ft
import serial
from configparser import ConfigParser
from time import sleep
from helpers import utils
import subprocess
import evdev
import threading
import os

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


# Check if the directory exists
snapshots_directory = "snapshots"
if not os.path.exists(snapshots_directory):
    # If it doesn't exist, create it
    os.makedirs(snapshots_directory)
    print(f"Created directory: {snapshots_directory}")
else:
    print(f"Directory already exists: {snapshots_directory}")


def WeighBridgeCtrl(page: ft.Page):
    # status changer
    def status(value: str, reason: None = ''):
        if value == 'busy':
            pb.visible = True
            status_icon.src = 'icons/yellow.png'
            status_value.value = 'PROCESSING'
        elif value == 'error':
            pb.visible = True
            status_icon.src = 'icons/red.png'
            status_value.value = f'Error. {reason}'
        else:
            status_icon.src = 'icons/green.png'
            pb.visible = False
            status_value.value = 'ready'
        page.update()
    # page preference
    page.window_full_screen = True
    page.fonts = {
        'Digital 7': 'https://www.1001fonts.com/download/font/digital-7.regular.ttf',
    }
    stat_value = ft.Text(
        '',
        size=120,
        font_family='Digital 7',
        color=ft.colors.GREEN_500,
    )
    status_value = ft.Text(
        'READY',
        size=30,
        font_family='Digital 7',
    )
    status_icon = ft.Image(src='icons/green.png')
    weight_value = ft.Text(
        '000000',
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
    pb = ft.ProgressBar(visible=False, height=50)
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
    def clear_defaults():
        while True:
            sleep(15)
            if weight_value.value == '000000':
                customer_value.value = '000000000'
                price_value.value = '0000.00'
                date_value.value = '00-00-0000'
                time_value.value = '00:00:00'
                plate_value.value = 'A0000'
                final_weight_value.value = '0'
                paid_value.value = 'UNKNOWN'
                stat_value.value = ''
                status('ready')
                page.update()
    clear = threading.Thread(target=clear_defaults)
    clear.start()
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
                                stat_value,
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
        pb,
    )
    # a loop reading data coming from serial port
    for device in [evdev.InputDevice(fn) for fn in evdev.list_devices()]:
        if device.name == 'Sycreader USB Reader':
            device = evdev.InputDevice(device.path)
            container = []
            device.grab()
            while True:
                try:
                    data = ser.read_all()
                    event = device.read_one()
                except OSError:
                    return page.window_close()
                if data:
                    status('busy')
                    weight_value.value = utils.sanitize(data)
                    page.update()
                if event and event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    digit = evdev.ecodes.KEY[event.code]
                    if digit == 'KEY_ENTER':
                        customer_value.value = ''.join(
                            i.strip('KEY_') for i in container
                        )
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
                        except subprocess.CalledProcessError:
                            status('error', reason='cant take snapshot')
                        # webhook implementation
                        if weight_value.value not in ['000000', '']:
                            utils.call_api(
                                endpoint=config.get('settings', 'webhook'),
                                weight=weight_value.value,
                                id=customer_value.value,
                                date=date_value.value,
                                time=time_value.value,
                                stat_value=stat_value,
                            )
                            status('ready')
                            page.update()
                    else:
                        container.append(digit)
        else:
            page.window_close()


# RUN IT BACK
ft.app(WeighBridgeCtrl, assets_dir='assets', name='Weight Reader')
