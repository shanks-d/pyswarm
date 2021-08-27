# pyswarm
Implementation of Spiral Mapping Algorithm using a Swarm of CrazyFlies.

## Setup
- Complete the installation for physical robots and simulation from the [documentation](https://crazyswarm.readthedocs.io/en/latest/installation.html)
- Git clone pyswarm and replace the scripts folder from `crazyswarm/ros_ws/src/crazyswarm/scripts` with `pyswarm/scripts`.
- Reconfigure the crazyflie addresses in the hexadecimal system and assign channels accordingly using a microUSB and cfclient
- Update the firmware of each crazyflie by following the steps mentioned [here](https://crazyswarm.readthedocs.io/en/latest/configuration.html)
- List all the crazyflies in the configuration file `allCrazyflies.yaml`. If you use unique marker arrangements, the `initialPosition` field of the `crazyflies.yaml` entries will be ignored, but if you use duplicated marker arrangements, `initialPosition` must be correct – a few centimeters variation is fine.
- Configure your motion capture system in the configuration ROS launch file `ros_ws/src/crazyswarm/launch/hover_swarm.launch`.
- You can enable/disable each crazyflie using the chooser tool. To start the chooser run:
```
cd ros_ws/src/crazyswarm/scripts
python chooser.py
```
Use python3 for ROS Noetic on Ubuntu 20.04.

## Tutorials
To run the test script in simulation:
```
python test_swarm.py --sim
```
In the 3D visualization, you should see the Crazyflies take off, complete the task, and then land.

To run the script on to real hardware, first start the `crazyswarm_server`:
```
roslaunch crazyswarm hover_swarm.launch
```
It should only take a few seconds to connect to the CFs. If you are using a motion capture system and `crazyswarm_server` is running correctly, you should be able to see CF pose(s) in `rviz`. 

Open a new terminal and run the script:
```
python swarm_flow.py
```
You should see the same behavior in real life. It is a good practice to run `chooser.py` before starting the `crazyswarm_server` to check the battery voltage of each crazyflie and rebooting the enabled CFs.