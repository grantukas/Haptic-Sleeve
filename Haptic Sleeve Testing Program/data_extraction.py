import os
import csv
import glob
import pandas as pd
import re

fname = "results*"
logfile_name_list = []
csv_name_list = []

print("Program started")

for file in glob.glob(fname):
    username = ""
    date = file[8:23]
    csv_name = ""
    logfile_name_list.append(file)

    # Search for username in all files to create csv filenames
    # First create the empty csv with the name, then write after csv is created
    with open(file, "r") as logfile:
        for line in logfile:
            if "User:" in line:
                username = line[47:].rstrip()
                csv_name = username + "_" + date + ".csv"
                csv_name_list .append(csv_name)
                with open(csv_name, "w"):
                    pass


for file, name in zip(logfile_name_list, csv_name_list):
    # To gather up all data for responses to write to csv at the end
    results_list = []
    results_list.append(["Test type", "Motor activation timestamp", "Response timestamp", "Actual activated motor",
                                       "Actual activation intensity", "Expected response", "User response"])
    # Add name and date to the top of the file with a blank row to separate
    results_list.append([name[:-20], name[-19:-11], "-", "-", "-", "-", "-"])
    results_list.append(["-", "-", "-", "-", "-", "-", "-"])
    # Read in logfile as a dataframe then convert to dict
    print("\nReading in data from " + file)
    df = pd.read_table(file, delimiter = " - ", names = ("Time", "Layer", "Function", "Message"), engine = 'python')
    dict = df.to_dict()

    # Start processing when test started is found
    # 3 entries for each command- Bleak GATT write, Direction sent, Direction pressed

    # For one row of data
    # Write username, date, get the test type
    # Get the timestamp from GATT write and store as "Motor activation timestamp"
    # Get the timestamp from direction pressed and store as "Response timestamp"
    # Get from "Direction sent" motor direction, store as "Actual activated motor", "Expected response" to W-A-S-D
    # Get from "Direction sent" motor intensity, store as "Actual activation intensity"
    # For all tests other than intensity test, "Expected response" is the same as "Actual activated motor"
    # Get from "Direction pressed" the user input

    # Only care about the timestamps and messages
    times = dict["Time"]
    messages = dict["Message"]

    # To get the indices of where each test is started
    index_list = []
    for index, message in messages.items():
        if message is not None and "test started" in message:
            index_list.append(str(index) + " " + message)

    # Step through each section of the results based on the starting indices of those sections
    # Every 3 lines is a new motor activation, 3 lines of data/motor activation
    # Ex. The first result for a test starts at line 70, so the next result starts at line 73
    # Set iterations in steps sizes of 3 (52 results, 3 lines per result, 52*3 = 156 number needed for 52 loops)
    print("Processing beginning for " + file)
    for test_index in index_list:
        # List comprehension to get integer index from the string
        test_start_index = [int(s) for s in test_index.split() if s.isdigit()][-1]
        test_type_iterations = 0

        if "Accuracy" in test_index: # Accuracy, speed + accuracy, 52 responses total
            test_type_iterations = 156
        elif re.search("^Speed.test", test_index.lstrip(str(test_start_index) + " ")): # 32 responses "Speed test"
            test_type_iterations = 96
        else: # Intensity test, 100 responses total
            test_type_iterations = 300

        # Step every 3 lines
        for j in range(0, test_type_iterations, 3):
            motor_timestamp = ""
            response_timestamp = ""
            actual_motor = ""
            intensity = ""
            expected_response = ""
            user_response = ""
            final_temp_list = []

            for i in range(1, 4):
                if i == 1: # First line contains the motor activation timestamp
                    motor_timestamp = times[test_start_index + i + j]
                if i == 2: # Second line contains the motor activated and intensity
                    actual_motor = messages[test_start_index + i + j][-4]
                    intensity = messages[test_start_index + i + j][-2]
                    # Convert number to WASD: 1 is W, 2- A, 3- S, 4- D
                    if actual_motor == "1":
                        expected_response = "w"
                    elif actual_motor == "2":
                        expected_response = "a"
                    elif actual_motor == "3":
                        expected_response = "s"
                    else:
                        expected_response = "d"
                if i == 3: # Third line contains the user's response
                    response_timestamp = times[test_start_index + i + j]
                    user_response = messages[test_start_index + i + j][-2]

            # Add the resulting information to the main temp list
            # This is adding the data as one row when written out to the CSV
            final_temp_list.extend([test_index, motor_timestamp, response_timestamp, actual_motor, intensity,
                                    expected_response, user_response])
            results_list.append(final_temp_list)

    # Write the data to a CSV file
    with open(name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(results_list)
        print("Data from " + file + " written to " + name)