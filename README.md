## WeighBridgeCtrl
This project is based on [COM-Watch](https://git.cubable.date/Stuff/COM-Watch) project which made initially

### How does it work
This program has a simple task
- When staff clicks on "Read" it will get the current weight of the dump truck using Serial connection through COM port
![Read](https://git.cubable.date/Stuff/WeighBridgeCtrl/raw/branch/main/assets/images/read.png)
- By clicking on "Push" the data will be pushed to a webhook (This can be used to calculate the weight of waste minus the weight of dump truck to get accurate weight of the waste that has been transferred to the station or it can do more)

![Push](https://git.cubable.date/Stuff/WeighBridgeCtrl/raw/branch/main/assets/images/push.png)
- Program is able to start automatically by putting a shortcut to the app inside [Startup Directory](https://support.microsoft.com/en-us/windows/add-an-app-to-run-automatically-at-startup-in-windows-10-150da165-dcd9-7230-517b-cf3c295d89dd) of Windows

### Development
- make sure you have python 3.7 and up
- make a virtual environment and install requirements mentioned in `requirements.txt`
- run `make build`