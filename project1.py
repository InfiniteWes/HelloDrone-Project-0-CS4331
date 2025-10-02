import logging
import sys
import time
import random
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# The following script initiates the drone, checks for the necessary sensor decks,
# and executes a simple takeoff and landing maneuver.

# Defining the URI
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# Event used to detect if the necessary deck it attached.
deck_attached_event = Event()

# Set logging level to suppress detailed debug logs
logging.basicConfig(level=logging.ERROR)

DEFAULT_HEIGHT = 0.5    # Default flight height in meters
BOX_LIMIT = 0.5         # Defines movement constraints
MAX_VEL = 0.5           # Defines the Maximum velocity of the drone.
MOVE_DURATION = 2       # Defines the seconds the drone stays in the destination before moving to a new destination.
MAX_RUN_TIME = 30       # Defines the maximum run time for the drone.

positions = []

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
def move_box_limit(scf):
    start = time.time()
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        while time.time() - start < MAX_RUN_TIME:
            x = random.uniform(-BOX_LIMIT, BOX_LIMIT)
            y = random.uniform(-BOX_LIMIT, BOX_LIMIT)

            positions.append((x, y))
            print(f"Moving to position: {x}, {y}")

            mc.start_linear_motion(x, y, 0)
            time.sleep(MOVE_DURATION)
        mc.stop()

def plot_path_positions():
    x_coords = [pos[0] for pos in positions]
    y_coords = [pos[1] for pos in positions]
    z_coords = [DEFAULT_HEIGHT] * len(positions)

    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot(x_coords, y_coords, z_coords, marker='o')
    ax.set_title("Drone Path in 3D")
    ax.set_xlabel("X Position (m)")
    ax.set_ylabel("Y Position (m)")
    ax.set_zlabel("Z Position (m)")
    ax.set_xlim([-BOX_LIMIT, BOX_LIMIT])
    ax.set_ylim([-BOX_LIMIT, BOX_LIMIT])
    ax.set_zlim([0, DEFAULT_HEIGHT])
    plt.show()

def take_off_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(3)
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

        move_box_limit(scf)

        plot_path_positions()