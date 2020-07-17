# Haptic Sleeve Testing Program
# By Grant Stankaitis
#
# Summary:
# This program is used to test the Haptic Sleeve.
# Commands are sent programmatically to test various scenarios.
# Everything is logged, so check the log file for analysis.
# When test cases are running, select ONLY numerical or alphabetical keys (NO arrow keys, enter, etc.).
# This is due to msvcrt.getche()- Reads a keypress, returns the resulting character; does not wait for Enter press.
#
# The 3 testing scenarios are:
# Accuracy, being able to correctly decipher the correct direction
# Speed, how quick the user can react to haptic feedback
# Intensity, can the user distinguish between different vibrational intensities?
#
# Directions:
# Accuracy: Press W-A-S-D keys for directions, NOT arrow keys
# W- Forward, A- Left, S- Back, D- Right
# Speed: User can pick any key to press, select ONLY numerical or alphabetical keys
# Intensity: User can select 1, 2, 3 to pick intensity level

import asyncio
import random
import logging
import msvcrt
from bleak import BleakClient

# Define UUIDs for Nordic UART Service
address = "3C:71:BF:FF:5E:5A" # Change the MAC address for your specific ESP32 here
UUID_NORDIC_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NORDIC_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Lists that contain commands to activate motors
# Command b"4,2" is interpreted as direction: 4, intensity: 2
# 4 possible directions, 3 possible intensity levels
# 1 is forward, 2 left, 3 back, 4 right
# 0,0 is all motors off
command_list = [b"1,2", b"2,2", b"3,2", b"4,2"]
command_list_intensity1 = [b"1,1", b"1,2", b"1,3"]
command_list_intensity2 = [b"2,1", b"2,2", b"2,3"]
command_list_intensity3 = [b"3,1", b"3,2", b"3,3"]
command_list_intensity4 = [b"4,1", b"4,2", b"4,3"]
command = b"0,0"

# Configure logging parameters
logging.basicConfig(filename="results.log", filemode="a", format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    level=logging.DEBUG)
logging.info("\n\n")
logging.info("PROGRAM BEGINS")


# Coroutine to run tests, based on which command list is picked to send from
# 50 loop iterations for accuracy, 30 for speed test 1, 50 for speed test 2, 30 for intensity
async def run_test(client, loop, command_list, loop_iterations):
    command_len = len(command_list)
    print("\nTest starting in: \n3")
    await asyncio.sleep(1.0, loop=loop)
    print("2")
    await asyncio.sleep(1.0, loop=loop)
    print("1")
    await asyncio.sleep(1.0, loop=loop)
    print("Start!")

    # All commands and keystrokes recorded
    previous_command = b""
    for i in range(loop_iterations):
        j = 0
        # Create temporary list to modify while iterating
        temp_command_list = command_list[:]
        while(j < command_len):
            # Choose/store a random command, make sure it isn't the same command randomly selected from previous loop
            # Remove command from list, then send command
            # Log command sent and log single keystroke from user
            motor_command = random.choice(temp_command_list)
            if motor_command != previous_command:
                temp_command_list.remove(motor_command)
                await client.write_gatt_char(UUID_NORDIC_TX, bytearray(motor_command[0:20]), True)
                logging.debug("Direction sent: " + str(motor_command))
                user_direction = msvcrt.getche()
                logging.debug("Key pressed: " + str(user_direction))
                previous_command = motor_command
                j += 1
    # Turn all motors off
    motor_command = command
    await client.write_gatt_char(UUID_NORDIC_TX, bytearray(motor_command[0:20]), True)
    logging.debug("ALL OFF, Direction sent: " + str(motor_command))
    print("\nDone!")


async def run_training(client):
    print("\nUser training started.")
    print("Select a vibrational intensity using 1, 2, or 3.")
    intensity = msvcrt.getche()
    print("\n Now select motor directions to activate using W-A-S-D. Q to quit.")

    # Wait on input from user and send command for appropriate keypress
    while(True):
        direction = msvcrt.getche()
        if direction == b"w": # Forward
            user_command = b"1," + intensity
            await client.write_gatt_char(UUID_NORDIC_TX, bytearray(user_command[0:20]), True)
        elif direction == b"a": # Left
            user_command = b"2," + intensity
            await client.write_gatt_char(UUID_NORDIC_TX, bytearray(user_command[0:20]), True)
        elif direction == b"s": # Back
            user_command = b"3," + intensity
            await client.write_gatt_char(UUID_NORDIC_TX, bytearray(user_command[0:20]), True)
        elif direction == b"d": # Right
            user_command = b"4," + intensity
            await client.write_gatt_char(UUID_NORDIC_TX, bytearray(user_command[0:20]), True)
        else: # All motors off and exit
            await client.write_gatt_char(UUID_NORDIC_TX, bytearray(command[0:20]), True)
            break


# Main coroutine
# Will attempt to connect to ESP32 via BLE MAC address
# Once connected, the program will then take user input to run tests
# The test cases are run as coroutines
# The main coroutine will wait on the test case coroutine before continuing the loop
async def main(address, loop):
    while True:  # Loop to allow reconnection
        try: # Attempt to connect to ESP32
            print("Connecting\n")
            async with BleakClient(address, loop=loop) as client:
                print("Connected!\n")
                print("Please input your name: ")
                username = input()
                logging.debug("User: " + username)
                while True: # Main loop, user selects test case
                    print("\n\nSelect the test you want to run then ENTER:")
                    print("1- Accuracy, 2- Speed")
                    print("3- Speed + Accuracy, 4- Intensity")
                    print("5- User Training, Any other int- QUIT")
                    select_test = int(input())

                    # Call coroutine function and wait on it to finish
                    if select_test == 1:
                        logging.debug("Accuracy test started")
                        await run_test(client, loop, command_list, 13)
                        # 13 loop iterations * 4 motor commands/iteration = 52 responses
                    elif select_test == 2:
                        logging.debug("Speed test started")
                        await run_test(client, loop, command_list, 8)
                        # 8 loop iterations * 4 motor commands/iteration = 32 responses
                    elif select_test == 3:
                        logging.debug("Speed + Accuracy test started")
                        await run_test(client, loop, command_list, 13)
                    elif select_test == 4:
                        logging.debug("Intensity test started")
                        # Testing intensity levels on each motor
                        await run_test(client, loop, command_list_intensity1, 8)
                        await run_test(client, loop, command_list_intensity2, 8)
                        await run_test(client, loop, command_list_intensity3, 8)
                        await run_test(client, loop, command_list_intensity4, 8)
                    elif select_test == 5:
                        logging.debug("User training started")
                        await run_training(client)
                    else:
                        break
                break
        except Exception as e: # Catch connection exceptions, usually "device not found," then try to reconnect
            print(e)
            print('Trying to reconnect...')
            continue


if __name__ == "__main__":
    # Create an event loop to run the main coroutine
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(address, loop))