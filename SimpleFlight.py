import logging
import sys
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

# The following script initiates the drone, checks for the necessary sensor decks,
# and executes a simple takeoff and landing maneuver.

# Defining the URI
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# Event used to detect if the necessary deck it attached.
deck_attached_event = Event()

# Set logging level to suppress detailed debug logs
logging.basicConfig(level=logging.ERROR)

# Default flight height in meters
DEFAULT_HEIGHT = 0.5

# Defines movement constraints
BOX_LIMIT = 0.5

"""
--------------------------------------
Callback function that checks if a specific sensor deck is attached.

Args:
    name (str): The name of the deck parameter.
    value_str (str): The value as a string, indicating whether the deck is detected.

If the deck is detected, an event is triggered.
"""

def param_deck_flow(name, value_str):
    value = int(value_str)
    if value:
        deck_attached_event.set()
        print(f'Deck {name} is attached!')
    else:
        print(f'Deck {name} is NOT attached!')

"""
Commands the drone to take off, hover for 3 seconds and then land.

Args:
    scf (SyncCrazyflie): Synchronized Crazyflie object for safe communication.
"""

def take_off_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(3)
        mc.stop()

def move_every_direction(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(3)  # Hover in place for 3 seconds

        # We can move in all directions
        print('Moving forward 0.1m')
        mc.forward(0.3)
        # Wait a bit
        time.sleep(1)
        print('Moving up 0.1m')
        mc.up(0.1)
    #    Wait a bit
        time.sleep(1)
        print('Rolling right 0.1m at 0.5 m/s and 270deg circle');
        mc.circle_right(0.1, velocity=0.5, angle_degrees=270)
        print('Moving down 0.1m')
        mc.down(0.3)
        # Wait a bit
        time.sleep(1)

        print('Rolling left 0.1m at 0.6m/s')
        mc.left(0.3, velocity=0.4)
        # Wait a bit
        time.sleep(1)
        print('Moving forward 0.1m')
        mc.forward(0.3)


        print("Landing...")
        mc.stop()  # Land the drone safel

def move_linear_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)
        mc.forward(0.5)
        time.sleep(1)
        mc.back(0.5)
        time.sleep(1)


def move_angular_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)
        mc.left(0.5)
        time.sleep(1)
        mc.right(0.5)
        time.sleep(1)
        mc.stop()

# -------------------------------------------------------

if __name__ == '__main__':
    print("Initializing drivers...")
    cflib.crtp.init_drivers()

    print("Connecting to Crazyflie...")
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        print("Connected!")

        # Add Callbacks to check if required decks are attached.
        scf.cf.param.add_update_callback(group="deck", name="bcFlow2", cb=param_deck_flow)
        scf.cf.param.add_update_callback(group="deck", name="bcMultiranger", cb=param_deck_flow)

        time.sleep(1)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected! Exiting...')
            sys.exit(1)

        # Execute move in all directions
        move_every_direction(scf)