# ESP32 Code
All of the code to run on the ESP32 lives here!

mainORIGINAL.py and bootORIGINAL.py contain the code from the original research project.
The files **main.py** and **boot.py** are the finalized files to be uploaded to the ESP32.
**boot.py** will run on every boot-up, importing the necessary modules, and configuring and activating BLE.
**main.py** will be executed after boot, containing the main code that sets up the Nordic UART Service and activates the motors when commands and received.
