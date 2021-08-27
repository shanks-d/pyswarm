"""Control the swarm. Useful to find the scaling parameters."""

from pycrazyswarm import Crazyswarm
import numpy as np


TAKEOFF_HEIGHT      = 0.5
TAKEOFF_DURATION    = 2
HOVER_DURATION      = 2
MOVE_DURATION       = 2
LAND_HEIGHT         = 0.05
LAND_DURATION       = 2


swarm = Crazyswarm()
timeHelper = swarm.timeHelper
cfs = swarm.allcfs.crazyflies


def takeoff():
    for cf in cfs:
        cf.takeoff(targetHeight=TAKEOFF_HEIGHT, duration=TAKEOFF_DURATION)
        # the drone actually moves when timeHelper.sleep is called
        timeHelper.sleep(TAKEOFF_DURATION + HOVER_DURATION)

def land():
    for cf in cfs:
        cf.land(targetHeight=LAND_HEIGHT, duration=LAND_DURATION)
        timeHelper.sleep(LAND_DURATION)

def move(pos):
    for cf in cfs:
        cf.goTo(goal=np.asarray(pos), yaw=0, duration=MOVE_DURATION)
        timeHelper.sleep(MOVE_DURATION + HOVER_DURATION)

def main():
    takeoff()
    move([0, 0.75, 0.5])
    move([0.75, 0.75, 0.5])
    land()

if __name__ == "__main__":
    main()
