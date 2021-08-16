"""Takeoff-hover-land for one CF. Useful to validate hardware config."""


from pycrazyswarm import Crazyswarm
import numpy as np
import random


TAKEOFF_DURATION = 1.0
DISPERSE_DURATION = 1.0
MOVE_DURATION = 0.5
RETURN_DURATION = 1.0
LAND_DURATION = 1.0


def disperse(cfs, timeHelper):
    pos = np.array([9, random.randint(1,8), 1])
    cfs[0].goTo(goal=pos.astype(float), yaw=0, duration=DISPERSE_DURATION)
    timeHelper.sleep(DISPERSE_DURATION)
    cfs[0].sense()

def updateMap(cfs):
    for k,cf in enumerate(cfs):
        cf.updateMap(k+1)

def printMap(cfs):
    for cf in cfs:
        print(cf.map)

def stopCondition(cfs):
    if cfs[0].case == 0:
        print("stop")
        return True
    else:
        return False

def check(cfs):
    print("checking case",cfs[0].case)
    
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
    pos = np.asarray(cfs[0].state.pos).round()

    print(pos)
    if cfs[0].move == 0:
        pos[1] -= 1.0
    elif cfs[0].move == 1:
        pos[0] -= 1.0
    elif cfs[0].move == 2:
        pos[0] += 1.0
    else:
        pos[1] += 1.0

    print(pos)
    cfs[0].goTo(goal=pos, yaw=0, duration=MOVE_DURATION)
    timeHelper.sleep(MOVE_DURATION)
    cfs[0].sense()
    # print("leftBound =",cfs[0].leftBound)
    # print("frontBound =",cfs[0].frontBound)
    # print("backBound =",cfs[0].backBound)
    # print("rightBound =",cfs[0].rightBound)


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
 
    updateMap(cfs)
    printMap(cfs)

    while 1:
        check(cfs)
        move(cfs)
    #     broadcast()
        updateMap(cfs)
        printMap(cfs)
        if stopCondition(cfs):
            break
    
    # hover
    print("Press any button to land...")
    swarm.input.waitUntilButtonPressed()

    pos = cfs[0].initialPosition
    pos[2] = 1.0
    cfs[0].goTo(goal=pos, yaw=0, duration=RETURN_DURATION)
    timeHelper.sleep(RETURN_DURATION)

    swarm.allcfs.land(targetHeight=0.0, duration=LAND_DURATION)
    timeHelper.sleep(LAND_DURATION)