## WeighBridgeCtrl
This project is based on [COM-Watch](https://git.cubable.date/Stuff/COM-Watch) project which made initially

### Requirements
- makes sure all hardware is attached properly
- run these commands for the first time:
    - to allow reading RFID device inputs and grabbing the device on lock:
        `sudo chown $USER -R /dev/input/`
    - to allow Weigh Bridge Unit to communicate with Pi on serial connection:
        `sudo usermod -a -G tty $USER && sudo usermod -a -G dialout $USER && sudo usermod -a -G uucp $USER`
### Development
- make sure you have python 3.7 and up
- make a virtual environment and install requirements mentioned in `requirements.txt`
- run `make build`
