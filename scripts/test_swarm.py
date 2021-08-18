"""Takeoff-hover-land for one CF. Useful to validate hardware config."""


from math import fabs
from pycrazyswarm import Crazyswarm
import numpy as np
import random
import sys, os


TAKEOFF_DURATION = 1
DISPERSE_DURATION = 1
MOVE_DURATION = 0.5
RETURN_DURATION = 1
LAND_DURATION = 1
simulation = True


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
        print(cf.id,(r+g+b))
        cf.setLEDColor(r,g,b)

def disperse(cfs, timeHelper):
    posSet = set()
    while not len(posSet) == len(cfs):
        pos = [(random.choice([1,9]), random.randint(2,8), 1), (random.randint(2,8), random.choice([1,9]), 1)]
        pos = random.choice(pos)
        posSet.add(pos)

    for cf in cfs:
        pos = np.array(posSet.pop())
        if simulation:
            cf.goTo(goal=pos.astype(float), yaw=0, duration=DISPERSE_DURATION)
            timeHelper.sleep(DISPERSE_DURATION)
        else:
            cf.updatePos(pos.astype(float))
        cf.sense()
    print("posSet:",posSet)


def adjustDir(cfs):
    for cf in cfs:
        if ((cf.case == [1, 1, 1, 0]).all()) or ((cf.case == [1, 1, 0, 0]).all()):
            cf.dir = 0
        elif ((cf.case == [1, 1, 0, 1]).all()) or ((cf.case == [1, 0, 0, 1]).all()):
            cf.dir = 3
        elif ((cf.case == [1, 0, 1, 1]).all()) or ((cf.case == [0, 0, 1, 1]).all()):
            cf.dir = 2
        elif ((cf.case == [0, 1, 1, 1]).all()) or ((cf.case == [0, 1, 1, 0]).all()):
            cf.dir = 1
        else:
            pass
            print("No wall near for drone id:",cf.id)
        # To adjust the case according to new Dir 
        cf.sense()

def updateMap(cfs):
    for k,cf in enumerate(cfs):
        cf.sense()
        cf.updateMap(k+1)

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
            for k in range(3):
                if cf.case[k] == 1:
                    cf.move = k
                    print("Drone id:",cf.id,"case:",cf.case,"dir:",cf.dir,"move:",cf.move)
                    break

def move(cfs,timeHelper):
    dronePos = set()
    # active = len(cfs) - sum((cf.stop for cf in cfs))
    for i, cf in enumerate(cfs):
        if cf.stop == False:
            pos = np.asarray(cf.state.pos).round()

            if (cf.dir == 3 and cf.move == 1) or (cf.dir == 0 and cf.move == 0) or (cf.dir == 2 and cf.move == 2):
                pos[0] += 1.0
            elif (cf.dir == 1 and cf.move == 1) or (cf.dir == 2 and cf.move == 0) or (cf.dir == 0 and cf.move == 2):
                pos[0] -= 1.0
            elif (cf.dir == 2 and cf.move == 1) or (cf.dir == 1 and cf.move == 2) or (cf.dir == 3 and cf.move == 0):
                pos[1] += 1.0
            elif (cf.dir == 0 and cf.move == 1) or (cf.dir == 1 and cf.move == 0) or (cf.dir == 3 and cf.move == 2):
                pos[1] -= 1.0
            else:
                pass
                print("Invalid move command")

            if cf.move == 0:
                cf.updateDir(-1)
            elif cf.move == 2:
                cf.updateDir(1)
            
            prevLength = len(dronePos)
            dronePos.add(tuple(pos))

            if len(dronePos) != prevLength:
                if simulation:
                    cf.goTo(goal=pos, yaw=0, duration=MOVE_DURATION)
                else:
                    cf.updatePos(pos.astype(float))
            else:
                if simulation:
                    cf.goTo(goal=cf.state.pos, yaw=0, duration=MOVE_DURATION)
                else:
                    cf.state.pos = cf.state.pos
                dronePos.add(cf.state.pos)
    if simulation:
        timeHelper.sleep(MOVE_DURATION, trail=True)

def main():
    # with HiddenPrints():
    arr = [0 if i>0 and i<10 and j>0 and j<10 else float('inf') for i in range(11) for j in range(11)]
    map = np.asarray(arr).reshape(11, 11)
    
    swarm = Crazyswarm(map)
    timeHelper = swarm.timeHelper
    cfs = swarm.allcfs.crazyflies
    getColors(cfs)
    if simulation:
        swarm.allcfs.takeoff(targetHeight=1.0, duration=TAKEOFF_DURATION)
        timeHelper.sleep(TAKEOFF_DURATION)
    disperse(cfs, timeHelper)
    adjustDir(cfs)
    # wait()    # Not needed in simulation
    
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

    if simulation:
        swarm.allcfs.land(targetHeight=0.0, duration=LAND_DURATION)
        timeHelper.sleep(LAND_DURATION)

    if len(np.where(map == 0)[0]) == 0:
        print("Task Completed")
        return True
    else:
        print("Task Failed")
        return False

if __name__ == "__main__":

    main()