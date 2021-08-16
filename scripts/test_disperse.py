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
    # pos = np.array([9, 7, 1])
    cfs[0].goTo(goal=pos.astype(float), yaw=0, duration=DISPERSE_DURATION)
    timeHelper.sleep(DISPERSE_DURATION)
    cfs[0].sense()

def adjustDir(cfs):
    print("Case",cfs[0].case)
    print("Dir",cfs[0].dir)
    print((cfs[0].case == [1, 1, 1, 0]).all())
    
    if ((cfs[0].case == [1, 1, 1, 0]).all()) or ((cfs[0].case == [1, 1, 0, 0]).all()):
        cfs[0].dir = 0
    elif ((cfs[0].case == [1, 1, 0, 1]).all()) or ((cfs[0].case == [1, 0, 0, 1]).all()):
        cfs[0].dir = 3
    elif ((cfs[0].case == [1, 0, 1, 1]).all()) or ((cfs[0].case == [0, 0, 1, 1]).all()):
        cfs[0].dir = 2
    else:
        print("No adjust in direction")
    cfs[0].sense()
    print("New dir",cfs[0].dir)
    print("New case",cfs[0].case)

def updateMap(cfs):
    for k,cf in enumerate(cfs):
        cf.sense()
        cf.updateMap(k+1)

def printMap(cfs):
    for cf in cfs:
        print(cf.map)

def stopCondition(cfs):
    if cfs[0].case.sum() == 0:
        print("Stop")
        return True
    else:
        return False

def check(cfs):
    print("Checking case",cfs[0].case)
    print("Dir",cfs[0].dir)
    
    for k in range(4):
        if k == 3:
            print("Stop condition in check()") 
            break
          
        if cfs[0].case[k] == 1:
            cfs[0].move = k
            print("Move",cfs[0].move)
            break

def move(cfs):
    pos = np.asarray(cfs[0].state.pos).round()
    print(pos)

    if (cfs[0].dir == 3 and cfs[0].move == 1) or (cfs[0].dir == 0 and cfs[0].move == 0) or (cfs[0].dir == 2 and cfs[0].move == 2):
        pos[0] += 1.0
    elif (cfs[0].dir == 1 and cfs[0].move == 1) or (cfs[0].dir == 2 and cfs[0].move == 0) or (cfs[0].dir == 0 and cfs[0].move == 2):
        pos[0] -= 1.0
    elif (cfs[0].dir == 2 and cfs[0].move == 1) or (cfs[0].dir == 1 and cfs[0].move == 2) or (cfs[0].dir == 3 and cfs[0].move == 0):
        pos[1] += 1.0
    elif (cfs[0].dir == 0 and cfs[0].move == 1) or (cfs[0].dir == 1 and cfs[0].move == 0) or (cfs[0].dir == 3 and cfs[0].move == 2):
        pos[1] -= 1.0
    else:
        print("Invalid move command")

    print(pos)
    cfs[0].goTo(goal=pos, yaw=0, duration=MOVE_DURATION)
    timeHelper.sleep(MOVE_DURATION)    
    
    if cfs[0].move == 0:
        cfs[0].updateDir(-1)
    elif cfs[0].move == 2:
        cfs[0].updateDir(1)


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
    adjustDir(cfs)
    # wait()    # Not needed in simulation
 
    updateMap(cfs)
    printMap(cfs)

    while 1:
        check(cfs)
        move(cfs)
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