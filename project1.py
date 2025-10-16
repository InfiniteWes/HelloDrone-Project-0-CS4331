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
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# # Event used to detect if the necessary deck it attached.
# REMEMBER TO UNCOMMENT
deck_attached_event = Event()

# # Set logging level to suppress detailed debug logs
# REMEMBER TO UNCOMMENT
logging.basicConfig(level=logging.ERROR)

DEFAULT_HEIGHT: float = 0.5    # Default flight height in meters
BOX_LIMIT: float = 0.5         # Defines movement constraints
MAX_VEL: float = 0.5           # Defines the Maximum velocity of the drone.
MOVE_DURATION: float = 2       # Defines the seconds the drone stays in the destination before moving to a new destination.
MAX_RUN_TIME: float = 30       # Defines the maximum run time for the drone.
MAX_DUMMIES = 2                #
INIT_POS: tuple = (0.0, 0.0)
NUM_MISSIONS: int = 2



def create_box(init_pos: tuple, dest: tuple) -> tuple:
    """
    Creates a relative virtual box based on the initial/final destination
    
    Args:
        init_pos (tuple): Initial position (x, y)
        dest (tuple): Destination position (x, y)
    
    Returns:
        tuple: (x_limit, y_limit) for the virtual box boundaries
    """
    init_x, init_y = init_pos
    dest_x, dest_y = dest
    
    # Calculate the boundaries needed to encompass both points
    x_limit = max(abs(init_x), abs(dest_x))
    y_limit = max(abs(init_y), abs(dest_y))
    
    # Ensure we don't exceed the global BOX_LIMIT
    x_limit = min(x_limit, BOX_LIMIT)
    y_limit = min(y_limit, BOX_LIMIT)
    
    return (x_limit, y_limit)

    
def generate_points(num_points: int, box: tuple) -> List:
    """
    Generate random n points within a given box 

    Args:
        num_points (int): amount of random points to generate
        box (tuple): x,y limits of virtual box

    Returns:
        w_points (List[tuple[float, float]]): random generated points to traverse 
    """

    w_points = []
    
    x_lim, y_lim = box  # new bounding box limits based on
    
    
    for _ in range(num_points):
        
        x = random.uniform(-x_lim, x_lim)
        y = random.uniform(-y_lim, y_lim)
        
        w_points.append((x, y))
    
    return w_points 
    

def create_path(r_wp: List[tuple], destination: tuple, box: tuple) -> List[tuple]:
    """
    Creates a complete path from waypoints and destination
    
    Args:
        r_wp (List[tuple]): List of waypoints
        destination (tuple): Final destination
        box (tuple): Box limits (x_limit, y_limit)
    
    Returns:
        List[tuple]: Complete path including initial position and destination
    """
    # Create a new list starting with INIT_POS
    drone_path = [INIT_POS] + r_wp + [destination]
    
    # Print the path
    for pt in drone_path:
        print(f"Going to point: {pt}")
    
    print(f"At final dest: {destination}")
    
    return drone_path



    ##################################################
    # -------------- UNCOMMENT THIS ---------------------

def param_deck_flow(name, value_str):
    """
    --------------------------------------
    Callback function that checks if a specific sensor deck is attached.

    Args:
        name (str): The name of the deck parameter.
        value_str (str): The value as a string, indicating whether the deck is detected.

    If the deck is detected, an event is triggered.
    """
    value = int(value_str)
    if value:
        deck_attached_event.set()
        print(f'Deck {name} is attached!')
    else:
        print(f'Deck {name} is NOT attached!')


def move_box_limit(scf, path: List[tuple]) -> List[tuple]:
    """
    Moves the drone through a series of points within the box limits
    
    Args:
        scf: SyncCrazyflie instance
        path (List[tuple]): List of (x,y) coordinates to traverse
    
    Returns:
        List[tuple]: List of positions visited for plotting
    """
    start = time.time()
    positions = []  # Store positions for plotting
    
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        for x, y in path:
            if time.time() - start > MAX_RUN_TIME:
                print("Maximum runtime reached!")
                break
                
            # Ensure point is within limits
            x = max(min(x, BOX_LIMIT), -BOX_LIMIT)
            y = max(min(y, BOX_LIMIT), -BOX_LIMIT)
            
            positions.append((x, y))
            print(f"Moving to position: ({x:.2f}, {y:.2f})")
            
            # Move to position
            mc.start_linear_motion(x, y, 0)
            time.sleep(MOVE_DURATION)
        
    
    return positions



def execute_mission(scf, destinations: List[tuple]):
    """
    Execute multiple missions with different destinations
    
    Args:
        scf: SyncCrazyflie instance
        destinations: List of (x,y) destination points to visit
    """
    all_positions = []  # Store all positions for final plotting
    
    for mission_num, dest in enumerate(destinations, 1):
        print(f"\n=== Starting Mission {mission_num} ===")
        print(f"From {INIT_POS} to {dest}")
        
        # Create path for this mission
        box = create_box(init_pos=INIT_POS, dest=dest)
        way_points = generate_points(2, box=box)
        curr_path = create_path(r_wp=way_points, destination=dest, box=box)
        
        # Execute path and store positions
        positions = move_box_limit(scf, curr_path)
        all_positions.extend(positions)
        
        
        print(f"=== Mission {mission_num} Completed ===")
    
    # Plot the complete path after all missions
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        mc.stop()
    plot_path_positions(all_positions)
    

    
    
    

def plot_path_positions(positions: List[tuple]):
    """
    Plots the path taken by the drone in 3D
    
    Args:
        positions (List[tuple]): List of (x,y) positions visited by the drone
    """
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

        destinations = [
            (0.4, -0.3),   # 1st destination
            (-0.3, 0.4),   # 2nd destination
  
        ]

        # Execute missions for each destination
        execute_mission(scf, destinations)



