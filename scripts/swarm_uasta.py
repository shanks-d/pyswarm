"""Physical implementation of spiral mapping algorithm using the Loco Positioning System in uASTA"""


from math import fabs
from pycrazyswarm import Crazyswarm
import numpy as np
import random
from time import sleep

# Map limits
mapBounds           = [7, 7]

# Drone attributes
TAKEOFF_HEIGHT      = 1.0
TAKEOFF_DURATION    = 5
DISPERSE_DURATION   = 6
MOVE_DURATION       = 2
LAND_HEIGHT         = 0.1
LAND_DURATION       = 3

# Scaling
# Actual world
adjust = 0.1
r_hat_min = np.array([0.0+adjust, 0.31, 0.0])
r_hat_max = np.array([2.32-adjust, 2.52, 2.0])
# Python world
r_max = np.array([mapBounds[0]-2, mapBounds[1]-2, 2])
r_min = np.array([1, 1, 0])
# Params
scale = (r_hat_max - r_hat_min)/(r_max - r_min)
offset = r_hat_min - scale*r_min


def scale2R(pos):
    return pos*scale + offset

def disperse(cfs, timeHelper):
    posSet = set()
    while not len(posSet) == len(cfs):
        pos = [(random.choice([1, mapBounds[0]-2]), random.randint(2, mapBounds[1]-3), 1), (random.randint(2, mapBounds[0]-3), random.choice([1, mapBounds[1]-2]), 1)]
        pos = random.choice(pos)
        posSet.add(pos)
    print("posSet:",posSet)
    
    for cf in cfs:
        pos = np.array(posSet.pop())
        cf.pose = pos.astype(float)        
        cf.goTo(goal=scale2R(cf.pose), yaw=0, duration=DISPERSE_DURATION)
    timeHelper.sleep(DISPERSE_DURATION)

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

def updateMap(cfs):
    for cf in cfs:
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
            cf.sense()
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
                cf.goTo(goal=scale2R(cf.pose), yaw=0, duration=MOVE_DURATION)
    timeHelper.sleep(MOVE_DURATION)

def stopSwarm(cfs, duration):
    sleep(duration)
    for cf in cfs:
        cf.cmdStop()

def main():
    arr = [0 if i>0 and i<mapBounds[0]-1 and j>0 and j<mapBounds[1]-1 else float('inf') for i in range(mapBounds[0]) for j in range(mapBounds[1])]
    map = np.asarray(arr).reshape(mapBounds[0], mapBounds[1])
    
    swarm = Crazyswarm(map)
    timeHelper = swarm.timeHelper
    cfs = swarm.allcfs.crazyflies

    # swarm.allcfs.takeoff(targetHeight=TAKEOFF_HEIGHT, duration=TAKEOFF_DURATION)
    # timeHelper.sleep(TAKEOFF_DURATION)

    for iter, cf in enumerate(cfs):
        cf.takeoff(TAKEOFF_HEIGHT + 0.3*iter, duration = TAKEOFF_DURATION)
    timeHelper.sleep(TAKEOFF_DURATION)
    
    disperse(cfs, timeHelper)
    iter = 0
    while 1:
        adjustDir(cfs)
        updateMap(cfs)
        print(map)
        
        while 1:
            check(cfs)
            move(cfs, timeHelper)
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
                cfs[0].goTo(goal=scale2R(leftover[0]), yaw=0, duration=MOVE_DURATION)
                cfs[1].goTo(goal=scale2R(leftover[-1]), yaw=0, duration=MOVE_DURATION)
                timeHelper.sleep(MOVE_DURATION)
            else:
                iter += 1
                if iter == 2:
                    print("Task Failed on second iteration")
                    print("Exiting...")
                    break
                cfs[0].stop = False
                cfs[0].goTo(goal=scale2R(leftover[0]), yaw=0, duration=MOVE_DURATION)
                timeHelper.sleep(MOVE_DURATION)
    
    # swarm.allcfs.land(targetHeight=LAND_HEIGHT, duration=LAND_DURATION)
    # timeHelper.sleep(LAND_DURATION)

    for cf in cfs:
        cf.land(targetHeight=LAND_HEIGHT, duration=LAND_DURATION)
    timeHelper.sleep(LAND_DURATION)
    
    stopSwarm(cfs, 2)


if __name__ == "__main__":

    main()