"""Takeoff-hover-land for one CF. Useful to validate hardware config."""


from math import fabs
from pycrazyswarm import Crazyswarm
import numpy as np
import random
import sys, os


TAKEOFF_DURATION    = 1
DISPERSE_DURATION   = 1
MOVE_DURATION       = 0.5
LAND_DURATION       = 1
SIMULATION          = False
PRINTS              = False
initMap             = None
posInit             = []
mapBounds           = [40, 10] 

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def getColors(cfs):
    for cf in cfs:
        r,g,b = random.random(), random.random(), random.random()
        cf.setLEDColor(r,g,b)

def disperse(cfs, timeHelper):
    global posInit
    posSet = set()
    while not len(posSet) == len(cfs):
        pos = [(random.choice([1, mapBounds[0]-1]), random.randint(2, mapBounds[1]-2), 1), (random.randint(2, mapBounds[0]-2), random.choice([1, mapBounds[1]-1]), 1)]
        pos = random.choice(pos)
        posSet.add(pos)
    print("posSet:",posSet)
    posInit = posSet.copy()
    posSet = {(1, 2, 1), (11, 9, 1), (14, 9, 1), (1, 4, 1), (39, 6, 1)}

    for cf in cfs:
        pos = np.array(posSet.pop())
        if SIMULATION:
            cf.goTo(goal=pos.astype(float), yaw=0, duration=DISPERSE_DURATION)
            timeHelper.sleep(DISPERSE_DURATION)
        else:
            cf.updatePos(pos.astype(float))
        cf.sense()

def adjustDir(cfs):
    for cf in cfs:
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
            pos = np.asarray(cf.state.pos).round()

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
                if SIMULATION:
                    cf.goTo(goal=pos, yaw=0, duration=MOVE_DURATION)
                else:
                    cf.updatePos(pos.astype(float))
    if SIMULATION:
        timeHelper.sleep(MOVE_DURATION, trail=True)

def task():
    arr = [0 if i>0 and i<mapBounds[0] and j>0 and j<mapBounds[1] else float('inf') for i in range(mapBounds[0] + 1) for j in range(mapBounds[1] + 1)]
    map = np.asarray(arr).reshape(mapBounds[0]+1, mapBounds[1]+1)
    
    swarm = Crazyswarm(map)
    timeHelper = swarm.timeHelper
    cfs = swarm.allcfs.crazyflies
    getColors(cfs)
    if SIMULATION:
        swarm.allcfs.takeoff(targetHeight=1.0, duration=TAKEOFF_DURATION)
        timeHelper.sleep(TAKEOFF_DURATION)
    disperse(cfs, timeHelper)
    iter = 0
    while 1:
        adjustDir(cfs)
        # wait()    # Not needed in SIMULATION
        
        updateMap(cfs)
        updateMap(cfs)
        initMap = map.copy()
        while 1:
            check(cfs)
            move(cfs, timeHelper)
            updateMap(cfs)
            updateMap(cfs)
            print(map)
            print(cfs[0].dir, cfs[1].dir)
            print(cfs[0].state.pos, cfs[1].state.pos)
            if stopCondition(cfs):
                break

        if len(np.where(map == 0)[0]) == 0:
            if SIMULATION:
                swarm.allcfs.land(targetHeight=0.0, duration=LAND_DURATION)
                timeHelper.sleep(LAND_DURATION)
            print("Task Completed")
            return True, None
        else:
            print("Task Failed on first iteration")
            leftover = np.where(map == 0)
            leftover = [(float(leftover[0][i]), float(leftover[1][i]), 1.0) for i in range(len(leftover[0]))]
            if len(leftover) > 1:
                cfs[0].stop, cfs[1].stop = False, False
                if SIMULATION:
                    cfs[0].goTo(goal=leftover[0], yaw=0, duration=MOVE_DURATION)
                    cfs[1].goTo(goal=leftover[-1], yaw=0, duration=MOVE_DURATION)
                    timeHelper.sleep(MOVE_DURATION, trail=True)
                else:
                    cfs[0].updatePos(leftover[0])
                    cfs[1].updatePos(leftover[-1])
            else:
                iter += 1
                if iter == 2:
                    return False, posInit
                cfs[0].stop = False
                if SIMULATION:
                    cfs[0].goTo(goal=leftover[0], yaw=0, duration=MOVE_DURATION)
                    timeHelper.sleep(MOVE_DURATION, trail=True)
                else:
                    cfs[0].updatePos(leftover[0])

def main():
    if PRINTS:
        return task()
    else:
        with HiddenPrints():
            return task()


if __name__ == "__main__":

    main()