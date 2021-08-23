#!/usr/bin/env python3

"""Testing the spiral mapping algorithm with one drone"""

import rospy
import tf
from geometry_msgs.msg import Pose, PoseStamped

import numpy as np
import random
import time

# ROS
rospy.init_node('publisher', anonymous=True)
pub = rospy.Publisher("/crazyflie/cmd_position", Pose, queue_size=1)
rate = rospy.Rate(30)
cmd = Pose()

# Drone attributes
id = 3
takeoffHeight = 1.0
landHeight = 0.1
startPos = np.array([5.0, 5.0])

# Scaling params
scale = np.array([0.3, 0.3]) 
offset = np.array([-0.41, -3.57])
threshold = np.array([0.03, 0.03])

# Map
arr = [0 if i>0 and i<10 and j>0 and j<10 else float('inf') for i in range(11) for j in range(11)]
map = np.asarray(arr).reshape(11, 11)

# Sensor data
case = np.ones(8)   # Left Front Right Back
pos = startPos.astype(int).copy()
state = np.zeros(2)
stateHeight = 0.0

# Bound following
command = -1   # 0 = Left, 2 = Front, 4 = Right, 6 = Back  **wrt drone**
dir = 2    # Initially faced front   **wrt world**
stop = False
dirDict = {0:2, 1:1, 2:0, 3:-1, 4:-2, 5:-3, 6:-4, 7:-5}
posDict = {-1:[0,0], 0:[0,-1], 1:[-1,-1], 2:[-1,0], 3:[-1,1], 4:[0,1], 5:[1,1], 6:[1,0], 7:[1,-1]}


def remapDir(x):
    return dirDict[x]

def increment(index, changeFactor):
    if index - changeFactor > 7:
        return index - changeFactor - 8
    elif index - changeFactor < 0:
        return index - changeFactor + 8
    else:
        return index - changeFactor

def sense():
    global case
    # Presence of bounds adjacent to pos
    # 0: Bound and 1: No Bound
    bound = np.zeros(8)
    loc = map[pos[0]-1:pos[0]+2, pos[1]-1:pos[1]+2].reshape(-1,)

    if loc[3] == 0: bound[0] = 1
    if loc[0] == 0: bound[1] = 1
    if loc[1] == 0: bound[2] = 1
    if loc[2] == 0: bound[3] = 1
    if loc[5] == 0: bound[4] = 1
    if loc[8] == 0: bound[5] = 1
    if loc[7] == 0: bound[6] = 1
    if loc[6] == 0: bound[7] = 1
    
    changeFactor = remapDir(dir)
    case = np.roll(bound, changeFactor)

    if 1 in case:
        commandIndex = (np.where(case == 1)[0][0])
        posIndex = increment(commandIndex, changeFactor)
    else:
        posIndex = -1
    return posDict[posIndex]

def disperse():
    global pos
    dispersePos = [(random.choice([1,9]), random.randint(2,8)), (random.randint(2,8), random.choice([1,9]))]
    # dispersePos = [1,1]
    dispersePos = random.choice(dispersePos)
    pos = np.asarray(dispersePos)
    rospy.loginfo("Starting Pos: %s",pos)

    pos = np.asarray(dispersePos)
    goTo(pos)
    sense()

def adjustDir():
    global dir
    if case[6] == 0 or (case[4] == 0 and case[6] == 0):
        dir = 0
    elif case[4] == 0 or (case[2] == 0 and case[4] == 0):
        dir = 6
    elif case[2] == 0 or (case[0] == 0 and case[2] == 0):
        dir = 4
    elif case[0] == 0 or (case[0] == 0 and case[6] == 0):
        dir = 2
    else:
        rospy.loginfo("No wall near the drone")
    # To adjust the case according to new Dir 
    sense()

def updateMap():
    global map
    map[pos[0]][pos[1]] = id

def stopCondition():
    if case.sum() == 0:
        rospy.loginfo("Stop drone id %s",id)
        return True
    else:
        return False

def check():
    global command
    sense()
    if not stopCondition():
        for k in range(8):
            if case[k] == 1:
                command = k

                rospy.loginfo("Drone id: %s",id)
                rospy.loginfo("dir: %s",dir)
                rospy.loginfo("command: %s",command)
                break

def move():
    global dir, pos
    if not stopCondition():

        # Find next pos relative to the current pos
        newPos = sense()
        pos[0] += newPos[0]
        pos[1] += newPos[1]

        # Change the dir according to the command
        newDir = remapDir(command)
        dir = increment(dir, newDir)
        
        goTo(pos)

def takeoff():
    global cmd
    scaledPos = pos*scale + offset
    cmd.position.x = scaledPos[0]
    cmd.position.y = scaledPos[1]
    cmd.position.z = takeoffHeight
    cmd.orientation.x = 0
    cmd.orientation.y = 0
    cmd.orientation.z = 0
    cmd.orientation.w = 1

    diff = abs(stateHeight - takeoffHeight)
    while diff > 0.05 and not rospy.is_shutdown():
        diff = abs(stateHeight - takeoffHeight)
        pub.publish(cmd)
        rate.sleep()

def land():
    global cmd
    cmd.position.z = landHeight
    diff = abs(stateHeight - landHeight)
    while diff > 0.05 and not rospy.is_shutdown():
        diff = abs(stateHeight - landHeight)
        pub.publish(cmd)
        rate.sleep()

def reached(goal):
    diff = np.abs(goal - state)
    # rospy.loginfo("diff: %s",diff)
    
    if (diff < threshold).all():
        return True
    else:
        return False

def goTo(goal):
    global cmd
    scaledGoal = goal*scale + offset
    cmd.position.x = scaledGoal[0]
    cmd.position.y = scaledGoal[1]
    cmd.orientation.x = 0
    cmd.orientation.y = 0
    cmd.orientation.z = 0
    cmd.orientation.w = 1

    while not reached(scaledGoal) and not rospy.is_shutdown():
        pub.publish(cmd)
        rate.sleep()

def callback(data):
    global state, stateHeight
    state[0] = data.pose.position.x
    state[1] = data.pose.position.y
    stateHeight = data.pose.position.z

def main():
    rospy.Subscriber("/crazyflie/pose", PoseStamped, callback) 

    rospy.loginfo("takeoff")
    takeoff()

    rospy.loginfo("disperse")
    disperse()
        
    adjustDir()
    # wait()    # Not yet needed
    
    updateMap()
    rospy.loginfo(map)

    while not rospy.is_shutdown():
        check()
        move()
        updateMap()
        rospy.loginfo(map)

        if stopCondition():
            break

    rospy.loginfo("land")
    land()

    if len(np.where(map == 0)[0]) == 0:
        rospy.loginfo("Task Completed")
        return True
    else:
        rospy.loginfo("Task Failed")
        return False


if __name__ == '__main__':
    
    main()
