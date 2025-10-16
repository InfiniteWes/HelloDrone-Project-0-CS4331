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

from typing import List, Any, Dict, Tuple

# The following script initiates the drone, checks for the necessary sensor decks,
# and executes a simple takeoff and landing maneuver.

# Defining the URI


# REMEMBER TO UNCOMMENT
# URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# # Event used to detect if the necessary deck it attached.
# REMEMBER TO UNCOMMENT
# deck_attached_event = Event()

# # Set logging level to suppress detailed debug logs
# REMEMBER TO UNCOMMENT
# logging.basicConfig(level=logging.ERROR)

DEFAULT_HEIGHT: float = 0.5    # Default flight height in meters
BOX_LIMIT: float = 0.5         # Defines movement constraints
MAX_VEL: float = 0.5           # Defines the Maximum velocity of the drone.
MOVE_DURATION: float = 2       # Defines the seconds the drone stays in the destination before moving to a new destination.
MAX_RUN_TIME: float = 30       # Defines the maximum run time for the drone.
INIT_POS: tuple = (0.0, 0.0)


def generate_points(num_points: int) -> List:
    """
    Generate n points within a box (0.5x0.5 for now)

    Args:
        num_points (int): amount of random points to generate

    Returns:
        w_points (List[tuple[float, float]]): random generated points to traverse 
    """

    w_points = []
    
    for _ in range(num_points-1):
        
        x = random.uniform(-BOX_LIMIT, BOX_LIMIT)
        y = random.uniform(-BOX_LIMIT, BOX_LIMIT)
        
        w_points.append((x, y))
    
    return w_points

def create_box(curr_pos: tuple, dest: tuple):
    
    x,y = 5, 6
    
    

def create_path(r_wp: List[tuple], destination: tuple):

    drone_path = r_wp.insert(0,INIT_POS)
    
    for pt in drone_path.it:
        print(f"Going to point: {pt}")
        
    else:
        
        print(f"At final dest: {destination}")  
        
    return drone_path 



    ##################################################
    # -------------- UNCOMMENT THIS ---------------------

# def param_deck_flow(name, value_str):
#   """
#   --------------------------------------
#   Callback function that checks if a specific sensor deck is attached.

#   Args:
#     name (str): The name of the deck parameter.
#     value_str (str): The value as a string, indicating whether the deck is detected.

#   If the deck is detected, an event is triggered.
#   """
#     value = int(value_str)
#     if value:
#         deck_attached_event.set()
#         print(f'Deck {name} is attached!')
#     else:
#         print(f'Deck {name} is NOT attached!')


# def move_box_limit(scf, destination: tuple):
#     start = time.time()
#     with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
#         while time.time() - start < MAX_RUN_TIME:
#             x = random.uniform(-BOX_LIMIT, BOX_LIMIT)
#             y = random.uniform(-BOX_LIMIT, BOX_LIMIT)

#             positions.append((x, y))
#             print(f"Moving to position: {x}, {y}")

#             mc.start_linear_motion(x, y, 0)
#             time.sleep(MOVE_DURATION)
#         mc.stop()

# def plot_path_positions():
#     x_coords = [pos[0] for pos in positions]
#     y_coords = [pos[1] for pos in positions]
#     z_coords = [DEFAULT_HEIGHT] * len(positions)

#     plt.figure()
#     ax = plt.axes(projection='3d')
#     ax.plot(x_coords, y_coords, z_coords, marker='o')
#     ax.set_title("Drone Path in 3D")
#     ax.set_xlabel("X Position (m)")
#     ax.set_ylabel("Y Position (m)")
#     ax.set_zlabel("Z Position (m)")
#     ax.set_xlim([-BOX_LIMIT, BOX_LIMIT])
#     ax.set_ylim([-BOX_LIMIT, BOX_LIMIT])
#     ax.set_zlim([0, DEFAULT_HEIGHT])
#     plt.show()

# def take_off_simple(scf):
#     with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
#         time.sleep(3)
#         mc.stop()

# -------------------------------------------------------

if __name__ == '__main__':
    # print("Initializing drivers...")
    # cflib.crtp.init_drivers()

    # print("Connecting to Crazyflie...")
    # with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    #     print("Connected!")

    #     # Add Callbacks to check if required decks are attached.
    #     scf.cf.param.add_update_callback(group="deck", name="bcFlow2", cb=param_deck_flow)
    #     scf.cf.param.add_update_callback(group="deck", name="bcMultiranger", cb=param_deck_flow)

    #     time.sleep(1)

    #     if not deck_attached_event.wait(timeout=5):
    #         print('No flow deck detected! Exiting...')
    #         sys.exit(1)

    #     move_box_limit(scf)

    #     plot_path_positions()

    
    print(f"================== BOX LIMIT {BOX_LIMIT} X -{BOX_LIMIT}================== \n")
    
    way_points = generate_points(4)
    curr_path = create_path(way_points, (-BOX_LIMIT, BOX_LIMIT))
    
    
    
    
