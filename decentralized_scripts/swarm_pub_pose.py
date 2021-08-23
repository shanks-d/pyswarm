#!/usr/bin/env python3

import rospy
import tf
from geometry_msgs.msg import Pose

if __name__ == '__main__':
    rospy.init_node('pub_pose', anonymous=True)
    x = 1
    y = -2
    z = 1

    rate = rospy.Rate(30)

    msg = Pose()
    msg.position.x = x
    msg.position.y = y
    msg.position.z = z
    quaternion = tf.transformations.quaternion_from_euler(0, 0, 0)
    msg.orientation.x = quaternion[0]
    msg.orientation.y = quaternion[1]
    msg.orientation.z = quaternion[2]
    msg.orientation.w = quaternion[3]

    pub = rospy.Publisher("/crazyflie/cmd_position", Pose, queue_size=1)

    # while not rospy.is_shutdown():
    rospy.loginfo("takeoff")
    count = 0
    while count < 250:
        pub.publish(msg)
        rate.sleep()
        count += 1
        rospy.loginfo(count)

    msg.position.z = 0.2
    rospy.loginfo("land")
    count = 0
    while count < 250:
        pub.publish(msg)
        rate.sleep()
        count += 1
        rospy.loginfo(count)