"""Physical implementation of spiral mapping algorithm using FlowDeck"""


from math import fabs
from pycrazyswarm import Crazyswarm
import numpy as np
import random
from time import sleep


# Map limits
mapBounds           = [10, 10]

# Drone attributes
TAKEOFF_HEIGHT      = 0.4
TAKEOFF_DURATION    = 2
HOVER_DURATION      = 1
DISPERSE_DURATION   = 4
MOVE_DURATION       = 2
LAND_HEIGHT         = 0.05
LAND_DURATION       = 2

# Scaling for FlowDeck
scale = np.array([0.75, 0.75, 0.5])

def scale2R(pos):
    return pos*scale

def disperse(cfs, timeHelper):
    posSet = set()
    while not len(posSet) == len(cfs):
        pos = [(random.choice([1, mapBounds[0]-2]), random.randint(2, mapBounds[1]-3), 1), (random.randint(2, mapBounds[0]-3), random.choice([1, mapBounds[1]-2]), 1)]
        pos = random.choice(pos)
        posSet.add(pos)
    print("posSet:",posSet)
    
    for i,cf in enumerate(cfs):
        cf.takeoff(targetHeight=TAKEOFF_HEIGHT, duration=TAKEOFF_DURATION)
        timeHelper.sleep(TAKEOFF_DURATION + HOVER_DURATION)
        pos = np.array(posSet.pop())
        cf.pose = pos.astype(float)        
        cf.goTo(goal=scale2R(cf.pose-cf.initialPosition), yaw=0, duration=DISPERSE_DURATION)
        timeHelper.sleep(DISPERSE_DURATION + HOVER_DURATION)

def adjustDir(cfs):
    for cf in cfs:
        cf.sense()
        if cf.case[6] == 0 or (cf.case[4] == 0 and cf.case[6] == 0):
            cf.dir = 0
        elif cf.case[4] == 0 or (cf.case[2] == 0 and cf.case[4] == 0):
            cf.dir = 6
        elif cf.case[2] == 0 or (cf.case[0] == 0 and cf.case[2] == 0):
            cf.dir = 4
        elif cf.case[0] == 0 or (cf.case[0] == 0 and cf.case[6] == 0):
            cf.dir = 2
        else:
            print("No wall near for drone id:",cf.id)
        # To adjust the case according to new Dir 
        cf.sense()
        print("Drone id:",cf.id,"dir:",cf.dir,"move:",cf.move)

def updateMap(cfs):
    for cf in cfs:
        cf.sense()
        cf.updateMap()

def stopCondition(cfs):
    stopFlags = []
    for cf in cfs:
        if cf.case.sum() == 0:
            print("Stop drone id:",cf.id)
            cf.stop = True
            stopFlags.append(True)
        else:
            stopFlags.append(False)
    return np.asarray(stopFlags).all()

def check(cfs):
    for cf in cfs:
        if cf.stop == False:
            for k in range(8):
                if cf.case[k] == 1:
                    cf.move = k
                    print("Drone id:",cf.id,"dir:",cf.dir,"move:",cf.move)
                    break

def move(cfs,timeHelper):
    dronePos = set()

    for cf in cfs:
        if cf.stop == False:
            pos = cf.pose.round()

            # Find next pos relative to the current pos
            newPos = cf.sense()
            pos[0] += newPos[0]
            pos[1] += newPos[1]

            # Change the dir according to the move
            newDir = cf.remapDir(cf.move)
            cf.dir = cf.increment(cf.dir, newDir)
            
            prevLength = len(dronePos)
            dronePos.add(tuple(pos))

            if len(dronePos) != prevLength:
                cf.pose = pos.astype(float)
                cf.goTo(goal=scale2R(cf.pose-cf.initialPosition), yaw=0, duration=MOVE_DURATION)
    timeHelper.sleep(MOVE_DURATION)

def takeoff(cfs, timeHelper):
    for cf in cfs:
        cf.takeoff(targetHeight=TAKEOFF_HEIGHT, duration=TAKEOFF_DURATION)
    timeHelper.sleep(TAKEOFF_DURATION + HOVER_DURATION)

def land(cfs, timeHelper):
    for cf in cfs:
        cf.land(targetHeight=LAND_HEIGHT, duration=LAND_DURATION)
    timeHelper.sleep(LAND_DURATION)

def stopSwarm(cfs):
    for cf in cfs:
        cf.cmdStop()

def main():
    arr = [0 if i>0 and i<mapBounds[0]-1 and j>0 and j<mapBounds[1]-1 else float('inf') for i in range(mapBounds[0]) for j in range(mapBounds[1])]
    map = np.asarray(arr).reshape(mapBounds[0], mapBounds[1])
    
    swarm = Crazyswarm(map)
    timeHelper = swarm.timeHelper
    cfs = swarm.allcfs.crazyflies

    # Takeoff didn't work when swarm.allcfs.takeoff() was used
    # takeoff(cfs, timeHelper)
    
    disperse(cfs, timeHelper)
    iter = 0
    
    while 1:
        adjustDir(cfs)
        updateMap(cfs)
        updateMap(cfs)
        print(map)
        
        while 1:
            check(cfs)
            move(cfs, timeHelper)
            updateMap(cfs)
            updateMap(cfs)
            print(map)
            if stopCondition(cfs):
                break

        if len(np.where(map == 0)[0]) == 0:
            print("Task Completed")
            break
        else:
            print("Task Failed on first iteration")
            print("Attempting Task again")
            leftover = np.where(map == 0)
            leftover = [(float(leftover[0][i]), float(leftover[1][i]), 1.0) for i in range(len(leftover[0]))]
            if len(leftover) > 1:
                cfs[0].stop, cfs[1].stop = False, False
                cfs[0].goTo(goal=scale2R(leftover[0]-cfs[0].initialPosition), yaw=0, duration=MOVE_DURATION)
                cfs[1].goTo(goal=scale2R(leftover[-1]-cfs[1].initialPosition), yaw=0, duration=MOVE_DURATION)
                timeHelper.sleep(MOVE_DURATION)
            else:
                iter += 1
                if iter == 2:
                    print("Task Failed on second iteration")
                    print("Exiting...")
                    break
                cfs[0].stop = False
                cfs[0].goTo(goal=scale2R(leftover[0]-cfs[0].initialPosition), yaw=0, duration=MOVE_DURATION)
                timeHelper.sleep(MOVE_DURATION)
    
    # Land did̈́n't work when swarm.allcfs.land() was used
    land(cfs, timeHelper)
    stopSwarm(cfs)


if __name__ == "__main__":

    main()