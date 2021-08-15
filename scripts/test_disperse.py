"""Takeoff-hover-land for one CF. Useful to validate hardware config."""


from pycrazyswarm import Crazyswarm
import numpy as np
import random


TAKEOFF_DURATION = 2.0
DISPERSE_DURATION = 3.0 


def disperse(cfs, timeHelper):
    pos1 = np.array([9, random.randint(1,8), 0])
    pos2 = np.array([random.randint(1,8), 9, 0])
    cfs[0].goTo(goal=pos1, yaw=0, duration=DISPERSE_DURATION)
    cfs[1].goTo(goal=pos2, yaw=0, duration=DISPERSE_DURATION)
    timeHelper.sleep(DISPERSE_DURATION)


if __name__ == "__main__":
    
    arr = [0 if i>0 and i<10 and j>0 and j<10 else float('inf') for i in range(11) for j in range(11)]
    temp = np.asarray(arr)
    map = temp.reshape(11, 11)
    
    swarm = Crazyswarm(map)
    timeHelper = swarm.timeHelper
    cfs = swarm.allcfs.crazyflies
    swarm.allcfs.takeoff(targetHeight=1.0, duration=TAKEOFF_DURATION)
    timeHelper.sleep(TAKEOFF_DURATION)
    disperse(cfs, timeHelper)
    # wait()    # Not needed in simulation

    map[int(cfs[0].state.pos[0])][int(cfs[0].state.pos[1])] = 1
    map[int(cfs[1].state.pos[0])][int(cfs[1].state.pos[1])] = 2
    print(map)    
    cfs[0].sense()
    print(cfs[0].frontBound)

    # while 1:
    #     check()
    #     move()
    #     broadcast()
    #     stop_condition()
    # hover()