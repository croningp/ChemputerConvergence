"""
This utility configures a Chemputer pump/valve after programming it.
It runs the user through the configuration in a dialog manner.
"""

# Import packages
import logging
from time import sleep
from ChemputerAPI import ChemputerPump, ChemputerValve
import sys

logging.basicConfig(level=logging.DEBUG, 
                    format="%(asctime)s ; %(levelname)s ; %(message)s")

while True:

    ###############################
    ### DIALOG & CONFIG SECTION ###
    ###############################

    # Ask for current IP address
    cur_ip = input("Please enter the current IP address: ")
    print("The current IP address is " + cur_ip)
    if cur_ip == '':
        cur_ip = '192.168.1.99'

    # Ask for new IP address
    while True:
        change_ip = input("Do you want to assign a new IP address? y/n ")
        if change_ip == 'y':
            new_ip = input("Please enter the IP address you're going to assign: ")
            print("The new IP address will be " + new_ip)
            break
        elif change_ip == 'n':
            new_ip = cur_ip
            print("The device will keep the IP address " + new_ip)
            break
        else:
            print("Oops! That was no valid input. Try again...y/n? ")

    # Ask for device type
    while True:
        device_type = input("Please enter p for pump or v for valve: ")
        if device_type == 'v':
            print("It's a valve. ")

            # Instantiate the device w/ current ip address
            valve = ChemputerValve(cur_ip, auto_init=False)
            sleep(0.5)
            valve.write_default_valve_configuration()
            sleep(0.5)

            # The valve should reply the values and confirm success
            # Next, errors are cleared:
            valve.clear_errors()
            sleep(0.5)

            # It is advisable to check if the device is now free of errors:
            valve.read_errors()
            sleep(0.5)

            # Manually move the valve between, no matter which positions exactly
            # just make sure its not precisely centred on one position)
            input("Ensure that valve is not precisley centred on one position. ")
            valve.auto_config()
            sleep(4)

            # Home valve
            valve.move_home()
            sleep(0.5)

            # Assign new ip address
            valve.assign_ip_address(new_ip)
            break
        elif device_type == 'p':
            print("It's a pump. ")

                    # Ask for syringe size
            while True:
                syr_sz = input("How many mL syringe? 10/25/50? ")
                if syr_sz in ["10", "25", "50"]:
                    print("Configure a" + syr_sz + "mL syringe")
                    break
                else:
                    print("Oops! That was no valid input. Try again...10/25/50? ")

            # Instantiate the device w/ current ip address
            pump = ChemputerPump(cur_ip, auto_init=False)
            sleep(0.5)

            # Write default config
            pump.write_default_pump_configuration(syringe_size=int(syr_sz))
            sleep(0.5)

            # Next, errors are cleared:
            pump.clear_errors()
            sleep(0.5)

            # It is advisable to check if the device is now free of errors:
            pump.read_errors()
            sleep(0.5)

            # Next, the home position should be determined:
            pump.hard_home(50); pump.wait_until_ready()
            sleep(0.5)

            # assign new ip address
            pump.assign_ip_address(new_ip)
            break
        else:
            print("Oops! That was no valid input. Try again...p/v? ")
    sleep(1.0)

    #######################
    ### TESTING SECTION ###
    #######################

    # Make a few moves and check if everything works
    if device_type == 'v':
        valve.move_home(); valve.wait_until_ready()
        valve.move_to_position(5); valve.wait_until_ready()
        valve.move_to_position(3); valve.wait_until_ready()
        valve.move_to_position(1); valve.wait_until_ready()
        valve.move_to_position(0); valve.wait_until_ready()
        valve.move_to_position(2); valve.wait_until_ready()
        valve.move_to_position(4); valve.wait_until_ready()
    else:
        pump.move_absolute(3, 50); pump.wait_until_ready()
        pump.move_relative(1, 50); pump.wait_until_ready()
        pump.move_relative(-3, 50); pump.wait_until_ready()
        pump.move_to_home(50); pump.wait_until_ready()

    # Configuration is done
    print("Setup SUCCESSFUL! ")

    #######################
    ### EXIT OR RESTART ###
    #######################

    # Configure another device or exit program
    while True:
        continue_config = input("Do you want to configure another device? y/n ")
        if continue_config == 'n':
            print("You can now close the window. ")
            break
        elif continue_config == 'y':
            print("Configure another device. ")
            break
        else:
            print("Oops! That was no valid input. Try again...y/n ?")

    if continue_config == 'n':
        break
    sleep(1)
    