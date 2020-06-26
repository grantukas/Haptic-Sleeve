# ESP32 Code
All of the code to run on the ESP32 lives here!

**esp32-idf4-20200617-unstable-v1.12-550-g4b5dd012e.bin** is the Micropython firmware to be flashed on the ESP32 board through uPyCraft. There may be a newer version available on the Micropython firmware download website. However, this is the version that I have been using/testing with and I can confirm that it is fully functioning for our requirements.

mainORIGINAL.py and bootORIGINAL.py contain the code from the original research project.

The files **main.py** and **boot.py** are the finalized files to be uploaded to the ESP32.
**boot.py** will run on every boot-up, importing the necessary modules, and configuring and activating BLE.
**main.py** will be executed after boot, containing the main code that sets up the Nordic UART Service and activates the motors when commands and received.

Files with a commit message **HERE FOR EARLIER TESTING** are files that were used during the testing process and are not being updated.
