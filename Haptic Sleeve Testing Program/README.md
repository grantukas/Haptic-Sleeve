# Haptic Sleeve Testing Program
The documentation for the program to test users with the Haptic Sleeve lives here. This readme will give a thorough description of the code.

# Data Extraction Program
This program was written to convert the log files from testing into CSV files. This is probably not the most efficient nor best-written way to achieve this, but I have tested it thoroughly and it works for our purposes. **Most importantly** this program was written with the asumption that test cases are not aborted mid test (ex. running an accuracy test and aborting the test at any point). **Each test case that is run must be run all the way through.** This is because each test case generates a specific number of results when completed fully, and the loops in the program are written to only handle that specific number of results, no less. For example, an accuracy test generates 52 entries or results, and there are 3 lines of data for each result, so ```52*3= 156 lines, 156 loop iterations```.

Additionally, you will need to install the module ```pandas``` for this program to work. This can be done using ```py -3 -m pip install pandas```.

## General functionality
This section contains an overview of the program. The program was tested on a Windows computer using Python 3.7.1, but I can additionally test on a Mac and work out bugs if needed.

The program uses Bleak to connect via BLE from a PC to the ESP32 on the Haptic Sleeve. Bleak is a GATT client software, capable of connecting to BLE devices acting as GATT servers. It is designed to provide an asynchronous, cross-platform Python API to connect and communicate with eg. sensors.

Because Bleak runs asynchronously, I opted to build the entire program to run asynchronously. I don't have much experience with asynchronous programming, so I found this to be a good exercise in learning asynchronous programming with Python.

Here's some background on asynchronous programming in Python. Usually, a program will run sequentially, meaning only one thing can be executed at a time. Python's ```asyncio``` module introduces asynchronous programming, which allows different tasks to start execution without waiting for the previous one to be completed.

Using asyncio, a coroutine is constructed that can be used to send commands to the Haptic Sleeve. A coroutine is a specialized version of a Python generator function. Coroutines are declared very similarly to Python functions:
```
async def run_test(client, loop, command_list):
```
The main function is also declared as a coroutine: ```async def main(address, loop):```

To start the main coroutine loop, an asyncio event loop is created, then the main coroutine is run using the created loop:
```
loop = asyncio.get_event_loop()
loop.run_until_complete(main(address, loop))
```

The main coroutine attempts to connect to the ESP32 using a BLE MAC address, and attempts to reconnect if it cannot find the device: 
```
try:
  ...
  async with BleakClient(address, loop=loop) as client:
    while True: # Main loop when device connected
    ...
  ...
except Exception as e: # Catch connection exceptions, usually "device not found," then try to reconnect
  ...
```

Once the device is connected, the user is presented with tests to run. When a test is selected, the test executes as a coroutine, and the main coroutine waits on the test to finish executing before completing the current loop iteration: ```await run_test(client, loop, command_list)```

The test cases send commands randomly from a list to the Haptic Sleeve by writing to the Nordic UART Service running on the ESP32:
```
motor_command = random.choice(temp_command_list)
temp_command_list.remove(motor_command)
await client.write_gatt_char(UUID_NORDIC_TX, bytearray(motor_command[0:20]), True)
logging.debug("Direction sent: " + str(motor_command))
user_direction = msvcrt.getche()
logging.debug("Key pressed: " + str(user_direction))
```

All input taken from the user and commands sent to the Haptic Sleeve are logged to a log file. The log file contains timestamps that can be used in our calculations, as well as other helpful information, like which commands were sent. An example log file (example.log) is here to show what information is conatined within a log file.

## Notes on the modules used
```asyncio``` is used to implement asynchronous programming.

```random``` is used to select commands randomly from a command list.

```logging``` is used to log output from the program.

**Important:**
```msvcrt``` gives access to a number of functions in the Microsoft Visual C/C++ Runtime Library. This is useful because it contains a function which will allow the program to read a single keypresses from the console.
```msvcrt.getche()``` is used to read a keypress and return the resulting character, and echo the character to the console. getche() will not wait for ```Enter``` to be pressed, which is useful for many reasons. For our purposes, this is useul because it allows the user to focus on pressing the appropriate keys during a test and not have to worry about pressing ```Enter``` after each input. Intuitively, this can be seen to be helpful during the speed test. ```msvcrt.getche()``` is only used during the tests, to begin a test the user must confirm their desired selection with the ```Enter``` key.
**Most importantly the user must select only alphabetical or numerical keys during a test. Special function keys will return ```\000```, then return the special key code. This is an issue because it means that it will return twice, which inadvertantly advances the test twice instead of once. Thus, it is easier to avoid this issue and use only alphabetical or numerical characters for input. Additionally, msvcrt *only works within a console window*, so the program must be run in a console window, like Windows cmd.**

## Setup
A few things are needed before running the program.

First, Bleak must be installed. Via Windows cmd this looks like:
```
py -3 -m pip install bleak
```
If you have trouble using pip, be sure that pip is enabled:
```
py -3 -m ensurepip
```
Additionally, this program **cannot** be run from IDLE (see *Notes on the modules used*, ```msvcrt``` module). It must be run via command line, or your IDE set to emulate the terminal in the output console. Be sure you are in the directory containing the program. To run via Windows cmd this looks like:
```
py -3 sleeve_test.py
```

## Usage
The program will attempt to connect to the Haptic Sleeve. If it cannot find the device, it will attempt to reconnect.

Once connected, the user will be presented with a menu to select which test they want to run, or quit the program. The selection is confirmed with the ```Enter``` key.

When a test starts, there will be a 3 second countdown before the first command is sent. When the test is running, the user can use the keyboard to input their responses based on what the test case requires. The user should **NOT** press the enter key during a test (as explained in *Notes on the modules used*, ```msvcrt``` module).

Once a test is completed, the program will return to the menu where a user can elect to run another test or quit the program.

A log file will be updated during execution of the program and can be used for analysis after tests.

## Test cases
The user can be given a few minutes to practice with the test cases to familiarize themselves with how the test cases are run.

### Accuracy test
The accuracy test is used to test if a user can accurately sense which motor is being activated. This test does not focus on the speed at which the user responds, but rather how accurately the user responds. The user should be instructed to use the W-A-S-D keys to input the direction, **not** the arrow keys (see *Notes on the modules used*, ```msvcrt``` module). W indicates forward, A indicates left, S indicates backwards, D indicates right.

A command will be sent randomly to one of the motors, with the next motor activated being any motor but the one that was previously activated. There will be a total of 52 motor activations. The motor activation commands are sent with an intensity level of 2, which is the middle value of the possible intensities (1, 2, 3)

### Speed test
The speed test is used to test how quickly a user can react to a motor being activated. This test focuses on the speed at which the user responds and is not concerned with if the user can accurately decipher which direction was sent. For this test, the user should be instructed to pick any one alphabetical or numerical key to press (see *Notes on the modules used*, ```msvcrt``` module). It is advisable for the user to stick with this key until the test concludes. This is to simplify the test so that it is only reliant on how quickly the user can respond/press one key.

Like the accuracy test, commands are randomly sent to each of the 4 motors with an intensity level of 2 , with 32 total commands sent.

### Speed + accuracy test
The speed + accuracy test is used to test how quickly *and* accurately a user can react to and sense a motor direction. This test will be used to gather data to see if the speed impacts how accurately a user can decipher motor directions.

Motors will be actiavated in the same fashion as previous tests, with 52 total motor activations.

### Intensity test
The intensity test is used to test if a user can decipher between the 3 intensity levels (1, 2, 3). The user should be instructed to select the numbers 1, 2, or 3 based on which intensity the user thinks is sent.

The intensity test is sent individually to each of the 4 motors. Each motor will be activated 24 times with varying intensities. After all 4 motors have been activated, the test concludes.

### User training
Before performing the tests, the user will have ~5 minutes to train with the Haptic Sleeve. First, the user will select an intensity for the motors to operate at. If the user wants to change intensities, they can select the E key to pick a new intensity level. Then, the program will wait on the user to input a direction using the W-A-S-D keys. A command will be sent to the corresponding motor. This way, the user can manually activate each motor as many times as they want to familiarize themselves with the haptic feedback directions.
