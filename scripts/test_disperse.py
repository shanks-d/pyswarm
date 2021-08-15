"""Takeoff-hover-land for one CF. Useful to validate hardware config."""


from pycrazyswarm import Crazyswarm
import numpy as np
import random


TAKEOFF_DURATION = 2.0
DISPERSE_DURATION = 3.0
MOVE_DURATION = 1.0
RETURN_DURATION = 3.0
LAND_DURATION = 2.0


def disperse(cfs, timeHelper):
    pos = np.array([9, random.randint(1,8), 1])
    cfs[0].goTo(goal=pos, yaw=0, duration=DISPERSE_DURATION)
    timeHelper.sleep(DISPERSE_DURATION)

def updateMap(cfs, map):
    for k,cf in enumerate(cfs):
        map[int(cfs[k].state.pos[0])][int(cfs[k].state.pos[1])] = k+1

def stopCondition(cfs):
    cfs[0].sense()
    print(cfs[0].leftBound)
    print(cfs[0].frontBound)
    print(cfs[0].backBound)
    print(cfs[0].rightBound)
    print(cfs[0].case)
    if cfs[0].case == 0:
        return True
    else:
        return False

def check(cfs):
    cfs[0].sense()
    print("checking case")
    
    if cfs[0].case == 1110:
        cfs[0].move = 2
    elif cfs[0].case == 111:
        cfs[0].move = 1
    elif cfs[0].case == 1011:
        cfs[0].move = 3
    elif cfs[0].case == 1101:
        cfs[0].move = 0
    
    elif cfs[0].case == 1100:
        cfs[0].move = 0
    elif cfs[0].case == 101:
        cfs[0].move = 1
    elif cfs[0].case == 11:
        cfs[0].move = 3
    elif cfs[0].case == 1010:
        cfs[0].move = 2
    
    elif cfs[0].case == 1000:
        cfs[0].move = 0
    elif cfs[0].case == 100:
        cfs[0].move = 1
    elif cfs[0].case == 1:
        cfs[0].move = 3
    elif cfs[0].case == 10:
        cfs[0].move = 2
    else:
        print("No condition for case =",cfs[0].case)

def move(cfs):
    pos = np.asarray(cfs[0].state.pos)

    print(pos)
    if cfs[0].move == 0:
        pos[1] -= 1
    elif cfs[0].move == 1:
        pos[0] -= 1
    elif cfs[0].move == 2:
        pos[0] += 1
    else:
        pos[1] += 1

    print(pos)
    cfs[0].goTo(goal=pos, yaw=0, duration=MOVE_DURATION)
    timeHelper.sleep(MOVE_DURATION)


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

    updateMap(cfs, map)
    print(map)


    while not stopCondition(cfs):
        check(cfs)
        move(cfs)
    #     broadcast()
        updateMap(cfs, map)
        print(map)
    
    # hover
    print("Press button to continue...")
    swarm.input.waitUntilButtonPressed()

    pos = cfs[0].initialPosition
    pos[2] = 1
    cfs[0].goTo(goal=pos, yaw=0, duration=RETURN_DURATION)
    timeHelper.sleep(RETURN_DURATION)

    swarm.allcfs.land(targetHeight=0.0, duration=LAND_DURATION)
    timeHelper.sleep(LAND_DURATION)