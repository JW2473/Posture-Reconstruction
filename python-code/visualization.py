#euler_order: roll, pitch, yaw
#original euler_order: yaw pitch roll
#euler_order in oriTrakHAR: roll yaw pitch
import numpy as np
import math
from pyquaternion import Quaternion
import transformations
import json
import matplotlib.pyplot as plt
import processData
from mpl_toolkits.mplot3d import Axes3D

ANGLE_MAP_L = json.load(open('leftDict_yzx.json', 'r'))
ANGLE_MAP_R = json.load(open('rightDict_yzx.json', 'r'))
fig = plt.figure()
ax = fig.gca(projection='3d')
interpolatedData = processData.processRow(['test.csv', 'test2.csv','test3.csv','test4.csv'], [5.5])
quatHead, quatLeft, quatRight, _, _, _ = next(interpolatedData)


def updateRealtimeVis(quat, idStr, ax):
    if idStr == 'head':
        headPos = quat.rotate([0, 0, 1])
        ind = np.linspace(0,1,11)
        x = [headPos[0]*i for i in ind]
        y = [headPos[1]*i for i in ind]
        z = [headPos[2]*i for i in ind]
        ax.plot(x, y, z)
        return quat

    euler = tf.transformations.euler_from_quaternion([quat[0], quat[1], quat[2], quat[3]])
    if idStr == 'rightArm':
        ans =  ANGLE_MAP_R[rad2Bucket(euler[0])][rad2Bucket(euler[2])][rad2Bucket(euler[1])]
        if ans.shoulderX is not None:
            elbowRelativeEuler = [deg2rad(ans.shoulderX), deg2rad(ans.shoulderZ), deg2rad(ans.shoulderY)]
            elbowRelativeQuat = transformations.quaternion_from_euler(elbowRelativeEuler[0], elbowRelativeEuler[1], elbowRelativeEuler[2])
            elbowRelativeQuat = Quaternion(elbowRelativeQuat)
            elbowPos = elbowRelativeQuat.rotate([0, -1, -1])
            wristRelativePos = quat.rotate([0, 0, -1])
            ind = np.linspace(0,1,11)
            x = [elbowPos[0]*i for i in ind] + [elbowPos[0]+wristRelativePos[0]*i for i in ind]
            y = [elbowPos[1]*i for i in ind] + [elbowPos[1]+wristRelativePos[1]*i for i in ind]
            z = [elbowPos[2]*i for i in ind] + [elbowPos[2]+wristRelativePos[2]*i for i in ind]
            ax.plot(x, y, z)
            return elbowRelativeQuat
        
    if idStr == 'leftArm':
        ans =  ANGLE_MAP_L[rad2Bucket(euler[0])][rad2Bucket(euler[2])][rad2Bucket(euler[1])]
        if ans.shoulderX is not None:
            elbowRelativeEuler = [deg2rad(ans.shoulderX), deg2rad(ans.shoulderZ), deg2rad(ans.shoulderY)]
            elbowRelativeQuat = transformations.quaternion_from_euler(elbowRelativeEuler[0], elbowRelativeEuler[1], elbowRelativeEuler[2])
            elbowRelativeQuat = Quaternion(elbowRelativeQuat)
            elbowPos = elbowRelativeQuat.rotate([0, 1, -1])
            wristPos = elbowPos + quat.rotate([0, 0, -1])
            ind = np.linspace(0,1,11)
            x = [elbowPos[0]*i for i in ind] + [elbowPos[0]+wristRelativePos[0]*i for i in ind]
            y = [elbowPos[1]*i for i in ind] + [elbowPos[1]+wristRelativePos[1]*i for i in ind]
            z = [elbowPos[2]*i for i in ind] + [elbowPos[2]+wristRelativePos[2]*i for i in ind]
            ax.plot(x, y, z)
            return elbowRelativeQuat

def rad2Bucket(rad):
    radInterval = 5*3.1415926/180
    ans = math.floor(rad / radInterval) * 5
    if ans == 180:
        return 180 - 5
    else:
        return ans

updateRealtimeVis(quatHead, 'head', ax)
plt.show()
