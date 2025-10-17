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

DEFAULT_HEIGHT = 0.5    # Default flight height in meters
BOX_LIMIT = 0.2         # Defines movement constraints
MAX_VEL = 0.5           # Defines the Maximum velocity of the drone.
MOVE_DURATION = 4       # Defines the seconds the drone stays in the destination before moving to a new destination.
MAX_RUN_TIME = 30       # Defines the maximum run time for the drone.
INIT_POS = (0.0, 0.0)
MAX_DUMMY = 2
NUMBER_OF_BOXES = 2

positions = []


def generate_dummy_waypoints(num_points: int) -> List[Tuple[float, float]]:
    """
    Generate n dummy waypoints within the current box constraints
    
    Args:
        num_points (int): amount of random points to generate
        
    Returns:
        w_points (List[Tuple[float, float]]): random generated points to traverse 
    """
    w_points = []
    
    for _ in range(num_points):
        x = random.uniform(-BOX_LIMIT, BOX_LIMIT)
        y = random.uniform(-BOX_LIMIT, BOX_LIMIT)
        w_points.append((x, y))
    
    return w_points

def get_next_destination() -> Tuple[float, float]:
    """
    Generate the next destination point outside current box
    This simulates moving to a new area/box
    
    Returns:
        Tuple[float, float]: Next destination coordinates
    """
    # For now, generate a point just outside current box
    # You can modify this logic based on project requirements
    x = random.choice([-BOX_LIMIT, BOX_LIMIT])
    y = random.choice([-BOX_LIMIT, BOX_LIMIT])
    return (x, y)

def create_path_with_waypoints_and_destination():
    """
    Create a complete path that includes:
    1. Dummy waypoints within current box
    2. Final destination (next box location)
    """
    path = []
    
    # Start at initial position
    path.append(INIT_POS)
    
    # Generate dummy waypoints for current box
    dummy_waypoints = generate_dummy_waypoints(MAX_DUMMY)
    
    # Add dummy waypoints to path
    for waypoint in dummy_waypoints:
        path.append(waypoint)
    
    # Get next destination (could be center of next box)
    next_destination = get_next_destination()
    path.append(next_destination)
    
    return path, dummy_waypoints, next_destination

def execute_waypoint_mission(scf):
    """
    Execute the mission with dummy waypoints and final destination
    """
    positions.append((0, 0, 0))  # Starting position
    
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        print("Starting waypoint mission...")
        
        # First destination: Run waypoint mission from current location
        for NUMBER_OF_BOXES in range(0, 2):  # Run mission twice
            print(f"\n=== MISSION {NUMBER_OF_BOXES} ===")

            # Create path for current mission
            full_path, dummy_waypoints, final_destination = create_path_with_waypoints_and_destination()
            
            # Loop through dummy waypoints
            print(f"Visiting {len(dummy_waypoints)} dummy waypoints...")
            for i, waypoint in enumerate(dummy_waypoints):
                x, y = waypoint
                positions.append((x, y))
                print(f"Moving to dummy waypoint {i+1}/{len(dummy_waypoints)}: ({x:.2f}, {y:.2f})")
                
                mc.start_linear_motion(x, y, 0)
                time.sleep(MOVE_DURATION)
            
            # Move to final destination
            dest_x, dest_y = final_destination
            positions.append((dest_x, dest_y))
            print(f"Moving to final destination: ({dest_x:.2f}, {dest_y:.2f})")
            
            mc.start_linear_motion(dest_x, dest_y, 0)
            time.sleep(MOVE_DURATION)

            print(f"Box {NUMBER_OF_BOXES} completed!")

        print("\nAll Boxes completed!")
        mc.stop() 

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


# def move_box_limit(scf):
#     start = time.time()
#     positions.append((0, 0, 0))
#     with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
#         while time.time() - start < MAX_RUN_TIME:
#             x = random.uniform(-BOX_LIMIT, BOX_LIMIT)
#             y = random.uniform(-BOX_LIMIT, BOX_LIMIT)
#             z = DEFAULT_HEIGHT

#             positions.append((x, y, z))
#             print(f"Moving to position: {x}, {y}, {z}")

#             mc.start_linear_motion(x, y, 0)
#             time.sleep(MOVE_DURATION)
#         mc.stop()

def plot_path_positions():
    x_coords = []
    y_coords = []
    z_coords = []
    
    for pos in positions:
        if len(pos) == 3:
            x, y, z = pos
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
        elif len(pos) == 2:
            x, y = pos
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(DEFAULT_HEIGHT)

    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot(x_coords, y_coords, z_coords, marker='o')
    
    # Highlight start point
    if len(x_coords) > 0:
        ax.scatter([x_coords[0]], [y_coords[0]], [z_coords[0]], 
                  color='green', s=100, label='Start')
    ax.scatter([x_coords[1]], [y_coords[1]], [z_coords[1]], color='blue', s=100, label='dummy')
    ax.scatter([x_coords[2]], [y_coords[2]], [z_coords[2]], color='blue', s=100, label='dummy')
    ax.scatter([x_coords[3]], [y_coords[3]], [z_coords[3]], color='purple', s=100, label='Intermediate Final')
    ax.scatter([x_coords[4]], [y_coords[4]], [z_coords[4]], color='blue', s=100, label='dummy')
    ax.scatter([x_coords[5]], [y_coords[5]], [z_coords[5]], color='blue', s=100, label='dummy')
    ax.scatter([x_coords[-1]], [y_coords[-1]], [z_coords[-1]], color='red', s=100, label='Final')

    ax.set_title("Drone Path in 3D")
    ax.set_xlabel("X Position (m)")
    ax.set_ylabel("Y Position (m)")
    ax.set_zlabel("Z Position (m)")
    
    # Set limits to show all points
    if x_coords and y_coords:
        ax.set_xlim([min(x_coords), max(x_coords)])
        ax.set_ylim([min(y_coords), max(y_coords)])
        ax.set_zlim([0, max(z_coords)])
    ax.legend()
    plt.show()

# def take_off_simple(scf):
#     with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
#         time.sleep(3)
#         mc.stop()

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

    # move_box_limit(scf)  # Original random movement
    execute_waypoint_mission(scf)

    plot_path_positions()