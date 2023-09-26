import contextlib
import re
import datetime
import subprocess
import urllib.request


class Utils:
    def __init__(self) -> None:
        pass

    def sanitize(self, in_bin):
        with contextlib.suppress(IndexError):
            bb = in_bin.decode(encoding='ascii', errors='ignore')
            clean = re.findall(r'\d{8}', bb)
            if not clean:
                return '000000'
            return clean[0][:-2]

    def time_now(self):
        current_datetime = datetime.datetime.now()
        return current_datetime.strftime('%d-%m-%Y'), current_datetime.strftime('%H:%M:%S')

    def camera_snapshot(
        self,
        ip: str,
        port: str,
        username: str,
        password: str,
        filename: str,
    ):
        wget_command = [
            'wget',
            '--http-user=' + username,
            '--http-password=' + password,
            '--output-document=' + 'snapshots/'+filename+'.jpeg',
            '--timeout=2',
            '--tries=1',
            f'http://{ip}:{port}/jpg/1/image.jpg',
        ]
        return subprocess.run(wget_command, check=True)

    def call_api(
        self,
        endpoint: str,
        weight: str,
        id: str,
        date: str,
        time: str,
    ):
        return urllib.request.urlopen(
            urllib.request.Request(
                endpoint.format(
                    weight,
                    id,
                    date,
                    time,
                ),
                headers={'User-Agent': 'Mozilla/5.0'},
            ),
        ).read()


utils = Utils()
