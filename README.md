# HelloDrone-Project-0-CS4331
This is the first project for our Cyber Aerial Computing Class
Authors: Wesley "2 balls" Spangler, Alejandro "Turd '2 ball' Ferguson" Rubio

---
## Project Overview
A Python script that demonstrates basic autonomous flight capabilities of a Crazyflie 2.1+ drone. The program performs a safety check for required sensor decks, then executes a basic takeoff-hover-land sequence.

## Features
- **Automatic deck detection**: Verifies that necessary sensor decks (Flow deck and Multiranger) are properly attached
- **Safe flight operations**: Uses the MotionCommander for simplified flight control
- **Error handling**: Exits gracefully if required hardware is not detected
- **Configurable parameters**: Easy to modify flight height and connection settings

## Hardware Requirements
- Crazyflie 2.1 drone
- Crazyradio PA (for wireless communication)
- Flow Deck v2 (for position estimation and stability)
- Multiranger deck (for obstacle detection)

## Flight Sequence
1. **Initialization**: Connects to the drone via radio link (connect dongle first and make sure firmware picks up on it)
2. **Hardware Check**: Verifies sensor decks are attached and functional  
3. **Takeoff**: Ascends to 0.5 meters height
4. **Hover**: Maintains stable flight for 3 seconds
5. **Landing**: Safely descends and stops motors

## Technical Details
- **Connection**: Uses radio protocol (default: `radio://0/80/2M/E7E7E7E7E7`)
- **Flight Height**: 0.5 meters (configurable via `DEFAULT_HEIGHT`)
- **Safety Timeout**: 5-second limit for deck detection
- **Logging**: Error-level logging to reduce console output

## Use Cases
- **Hardware testing**: Verify drone and sensor functionality
- **Development base**: Starting point for more complex flight patterns
- **Demonstration**: Simple autonomous flight for presentations

## Getting Started
1. Ensure Crazyflie is powered and connected
2. Verify sensor decks are properly mounted
3. Run the script - it will automatically handle connection and flight
4. The drone will take off, hover briefly, then land automatically

---

**NOTE:** There are 3 files I added, even though the `src code` from the prof. is a combination of the 2, thought why not just add them anyways. \
Also, I know we work in `crazyflie-clients-python/<dir>` but only src code should go in the repo? &larr; (Delete me after answered)
```
connect_log_param.py        # From: https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_connect_log_param/
motion_flying.py            # From: https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_motion_commander/
Hello_drone.py              # From: Prof. src code
```


