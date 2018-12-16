#euler_order: roll, pitch, yaw
#original euler_order: yaw pitch roll
#euler_order in oriTrakHAR: roll yaw pitch
import math
from pyquaternion import Quaternion
import tf
import json

ANGLE_MAP_L = json.load(open('leftDict_yzx.json', 'r'))
ANGLE_MAP_R = json.load(open('rightDict_yzx.json', 'r'))
def updateRealtimeVis(quat, idStr):
    if idStr == 'head':
        return quat
        #to be done
    if idStr == 'rightArm':
        euler = tf.transformations.euler_from_quaternion(quat)
        ans =  ANGLE_MAP_R[rad2Bucket(euler[0])][rad2Bucket(euler[2])][rad2Bucket(euler[1])]
        if ans.shoulderX is not None:
            elbowRelativeEuler = [deg2rad(ans.shoulderX), deg2rad(ans.shoulderZ), deg2rad(ans.shoulderY)]
            elbowRelativeQuat = tf.transformations.quaternion_from_euler(elbowRelativeEuler)
            elbowRelativeQuat = Quaternion(elbowRelativeQuat)
            return elbowRelativeQuat
        #to be done
    if idStr == 'leftArm':
        ans =  ANGLE_MAP_L[rad2Bucket(euler[0])][rad2Bucket(euler[2])][rad2Bucket(euler[1])]
        if ans.shoulderX is not None:
            elbowRelativeEuler = [deg2rad(ans.shoulderX), deg2rad(ans.shoulderZ), deg2rad(ans.shoulderY)]
            elbowRelativeQuat = tf.transformations.quaternion_from_euler(elbowRelativeEuler)
            elbowRelativeQuat = Quaternion(elbowRelativeQuat)
            return elbowRelativeQuat
        #to be done

def rad2Bucket(rad):
    radInterval = 5*3.1415926/180
    ans = math.floor(rad / radInterval) * 5
    if ans == 180:
        return 180 - 5
    else:
        return ans
