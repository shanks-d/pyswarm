"""Takeoff-hover-land for one CF. Useful to validate hardware config."""


from pycrazyswarm import Crazyswarm
import numpy as np
import random


def disperse(cfs, timeHelper):
    for cf in cfs:
        posX, posY, posZ = np.array(cf.state.pos)
        X, Y, Z = random.random(), random.random(), 0
        while posX >= 0 and posY >= 0 and posX <= 10 and posY <= 10:
            posX, posY, posZ = np.array(cf.state.pos) + np.array([X, Y, 0])
            pos = np.array([posX, posY, posZ])
            print(pos)
            cf.cmdPosition(pos)
            timeHelper.sleep(0.1)


if __name__ == "__main__":
    
    arr = [0 if i>0 and i<10 and j>0 and j<10 else float('inf') for i in range(11) for j in range(11)]
    temp = np.asarray(arr)
    map = temp.reshape(11, 11)
    
    swarm = Crazyswarm(map)
    timeHelper = swarm.timeHelper
    cfs = swarm.allcfs.crazyflies
    swarm.allcfs.takeoff(targetHeight=1.0, duration=1.0)
    timeHelper.sleep(2)
    disperse(cfs, timeHelper)

    print(map)
    left, right, front, back = cfs[0].sense()
    print(left, right, front, back)

    # takeoff()
    # disperse()
    # wait()
    # while 1:
    #     check()
    #     move()
    #     broadcast()
    #     stop_condition()
    # hover()