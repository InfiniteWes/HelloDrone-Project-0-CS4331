"""
Example script that allows a user to "push" the Crazyflie 2.1+ around 
using their hands while it's hovering.
This example uses the Flow and Multi-ranger decks to measure distances
in all directions and tries to keep away from anything that comes closer
than 0.2m by setting a velocity in the opposite direction.
The demo is ended by either pressing Ctrl-C or by holding your hand above the
Crazyflie.
"""
import logging
import sys
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.utils.multiranger import Multiranger
import random

# Define the default URI for communication with the Crazyflie
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E5')

BOX_LIMIT = 0.5          # Box Limit / Boundary Area
VELOCITY = 0.1           # Velocity of the drone
MINIMUM_HEIGHT = 0.3
AVOID_LATERAL = 0.5
SIDESTEP_TIME = 1
LOOP_DT = 0.1            # main loop sleep time

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

"""---------------------------------------------------------------------------"""
""" 
Check if an object is too close to the drone.
Args:
    range (float or None): Distance measured by the sensor.
Returns:
    bool: True if the object is closer than the minimum distance, otherwise False.
"""
def is_close(range):
    MIN_DISTANCE = 0.2  # Minimum allowed distance in meters
    if range is None:  # If no valid distance is detected, return False
        return False
    else:
        return range < MIN_DISTANCE  # Return True if the object is within the limit

"""---------------------------------------------------------------------------"""
if __name__ == '__main__':
    # Initialize the low-level drivers for Crazyflie communication
    cflib.crtp.init_drivers()

    # Create a Crazyflie object with a cache for parameters
    cf = Crazyflie(rw_cache='./cache')

    # Establish a synchronous connection to the Crazyflie
    with SyncCrazyflie(URI, cf=cf) as scf:
        # Send an arming request to enable the drone for flight
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)  # Wait for arming process to complete

        # Enter motion control mode
        with MotionCommander(scf, default_height=MINIMUM_HEIGHT) as motion_commander:
            # Activate the Multi-ranger deck for distance sensing
            with Multiranger(scf) as multiranger:
                # Compute total time we need to drive forward to cover RACE_DISTANCE
                total_time_needed = 190
                start_time = time.time()

                try:
                    # Start driving forward immediately
                    motion_commander.start_linear_motion(VELOCITY, 0.0, 0.0)

                    while True:
                        elapsed = time.time() - start_time
                        # Finish line reached
                        if elapsed >= total_time_needed:
                            break

                        # Emergency: object above us -> stop race and land
                        if is_close(multiranger.up):
                            print('Object detected above — stopping race')
                            break

                        # If obstacle in front, perform sidestep while continuing forward
                        if is_close(multiranger.front):
                            # Choose clearer side: prefer the side with larger reported distance
                            # Treat None as very large (no obstacle)
                            left = multiranger.left if multiranger.left is not None else 10.0
                            right = multiranger.right if multiranger.right is not None else 10.0

                            if left == right:
                                # Tie or both None -> pick a random side
                                side = random.choice(['left', 'right'])
                            else:
                                side = 'left' if left > right else 'right'

                            lateral = AVOID_LATERAL if side == 'left' else -AVOID_LATERAL
                            print(f'Front obstacle detected — sidestepping {side}')

                            # Start sidestep: keep forward speed and add lateral component
                            motion_commander.start_linear_motion(VELOCITY, lateral, 0.0)

                            # Continue sidestepping for SIDESTEP_TIME or until front is clear
                            sidestart = time.time()
                            while time.time() - sidestart < SIDESTEP_TIME:
                                # If an object appears above during sidestep, abort
                                if is_close(multiranger.up):
                                    print('Object detected above during sidestep — aborting')
                                    raise KeyboardInterrupt
                                # If front cleared sufficiently, break early
                                if not is_close(multiranger.front):
                                    break
                                time.sleep(LOOP_DT)

                            # Resume straight forward
                            motion_commander.start_linear_motion(VELOCITY, 0.0, 0.0)

                        # No front obstacle -> continue forward (ensure setpoint active)
                        time.sleep(LOOP_DT)

                except KeyboardInterrupt:
                    # User requested abort (Ctrl-C)
                    print('Keyboard interrupt received — stopping and landing')

                finally:
                    # Stop horizontal motion and allow motion commander context to land
                    try:
                        motion_commander.stop()
                    except Exception:
                        pass

                print('Race finished or aborted — demo terminated!')