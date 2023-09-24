import contextlib
import re
import datetime
import subprocess


class Utils:
    def __init__(self) -> None:
        pass
    def sanitize(self, in_bin):
        with contextlib.suppress(IndexError):
            bb = in_bin.decode(encoding='ascii', errors='ignore')
            clean = re.findall(r'\d{8}', bb)
            return clean[0][:-2]

    def time_now(self):
        current_datetime = datetime.datetime.now()
        return current_datetime.strftime('%d-%m-%Y'),current_datetime.strftime('%H:%M:%S')
    
    def camera_snapshot(self, ip, port, username, password, filename):
        wget_command = [
            "wget",
            "--http-user=" + username,
            "--http-password=" + password,
            "--output-document=" + "snapshots/"+filename+".jpeg",
            f"http://{ip}:{port}/jpg/1/image.jpg",
        ]
        return subprocess.run(wget_command, check=True)

utils = Utils()
