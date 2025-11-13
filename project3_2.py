"""
Example script that allows the Crazyflie to follow a 1-meter forward path
while avoiding obstacles using the Multi-ranger deck.
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
from threading import Event

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E5')
logging.basicConfig(level=logging.ERROR)

deck_attached_event = Event()


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

# ---------------------------------------------------------------------------
def is_close(range_value):
    """Check if an object is too close to the drone."""
    MIN_DISTANCE = 0.3  # Increased for better obstacle avoidance
    if range_value is None:
        return False
    else:
        return range_value < MIN_DISTANCE
# ---------------------------------------------------------------------------


if __name__ == '__main__':
    cflib.crtp.init_drivers()
    cf = Crazyflie(rw_cache='./cache')

    with SyncCrazyflie(URI, cf=cf) as scf:
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        with MotionCommander(scf, default_height=0.2) as motion_commander:
            with Multiranger(scf) as multiranger:
                
                # Goal parameters
                TARGET_DISTANCE = 1.0  # 1 meter forward
                distance_traveled = 0.0
                start_time = time.time()
                
                # Movement parameters
                FORWARD_VELOCITY = 0.1  # Base forward speed
                AVOIDANCE_VELOCITY = 0.1  # Speed for obstacle avoidance
                
                print('Starting path following...')
                keep_flying = True

                while keep_flying and distance_traveled < TARGET_DISTANCE:
                    # Default: move forward toward goal
                    velocity_x = FORWARD_VELOCITY
                    velocity_y = 0.0
                    
                    # Obstacle avoidance takes priority
                    obstacle_detected = False
                    
                    if is_close(multiranger.front):
                        print('Obstacle ahead! Stopping forward movement.')
                        velocity_x = 0.0
                        obstacle_detected = True
                        
                        # Try to go around the obstacle
                        if not is_close(multiranger.left):
                            velocity_y = AVOIDANCE_VELOCITY  # Move left
                            print('Moving left to avoid')
                        elif not is_close(multiranger.right):
                            velocity_y = -AVOIDANCE_VELOCITY  # Move right
                            print('Moving right to avoid')
                        else:
                            velocity_x = -AVOIDANCE_VELOCITY  # Move back
                            print('Moving backward to avoid')
                    
                    if is_close(multiranger.left):
                        velocity_y -= AVOIDANCE_VELOCITY  # Move right
                        obstacle_detected = True
                        
                    if is_close(multiranger.right):
                        velocity_y += AVOIDANCE_VELOCITY  # Move left
                        obstacle_detected = True
                    
                    if is_close(multiranger.back):
                        velocity_x += AVOIDANCE_VELOCITY  # Move forward
                        obstacle_detected = True
                    
                    # Stop if object detected above
                    if is_close(multiranger.up):
                        print('Object above detected - landing!')
                        keep_flying = False
                        break
                    
                    # Apply velocity
                    motion_commander.start_linear_motion(velocity_x, velocity_y, 0)
                    
                    # Estimate distance traveled (only count forward movement)
                    if velocity_x > 0 and not obstacle_detected:
                        distance_traveled += velocity_x * 0.1
                    
                    print(f'Distance: {distance_traveled:.2f}m / {TARGET_DISTANCE}m')
                    
                    time.sleep(0.1)
                
                # Stop at the end
                motion_commander.start_linear_motion(0, 0, 0)
                print(f'Path complete! Traveled: {distance_traveled:.2f}m')
                time.sleep(1.0)

                print('Demo terminated!')