"""Takeoff-hover-land for one CF. Useful to validate hardware config."""

from pycrazyswarm import Crazyswarm
import numpy as np


def main():

    arr = [0 if i>0 and i<10 and j>0 and j<10 else float('inf') for i in range(11) for j in range(11)]
    temp = np.asarray(arr)
    map = temp.reshape(11, 11)

    swarm = Crazyswarm(map)
    timeHelper = swarm.timeHelper
    cf = swarm.allcfs.crazyflies[0]
    
    print(map)
    left, right, front, back = cf.sense()
    print(left, right, front, back)


if __name__ == "__main__":
    main()
    # takeoff()
    # disperse()
    # wait()
    # while 1:
    #     check()
    #     move()
    #     broadcast()
    #     stop_condition()
    # hover()