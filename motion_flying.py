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


URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
deck_attached_event = Event()

DEFAULT_HEIGHT = 0.5
BOX_LIMIT = 0.5

def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')

# STEP 2: Take off function
def take_off_simple(scf):

    with MotionCommander(scf) as mc:
        mc.up(0.3)
        time.sleep(3)
        mc.stop()

def move_linear_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)
        mc.forward(0.5)
        time.sleep(1)
        mc.back(0.5)
        time.sleep(1)


if __name__ == '__main__':

    cflib.crtp.init_drivers()

    # STEP 1: Security before flying
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.cf.param.add_update_callback(group="deck", name="bcFlow2",cb=param_deck_flow)


        # If this returns false, the function will not be called and the crazyflie will not take off
        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)

            # Arm the Crazyflie
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        take_off_simple(scf)