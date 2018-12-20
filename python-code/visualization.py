#euler_order: roll, pitch, yaw
#original euler_order: yaw pitch roll
#euler_order in oriTrakHAR: roll yaw pitch
import numpy as np
import math
import time
from pyquaternion import Quaternion
import transformations
import json
import matplotlib.pyplot as plt
from processStream import processRow
from mpl_toolkits.mplot3d import Axes3D

ANGLE_MAP_L = json.load(open('leftDict_yzx.json', 'r'))
ANGLE_MAP_R = json.load(open('rightDict_yzx.json', 'r'))
plt.ion()
fig = plt.figure()
ax = fig.gca(projection='3d')
t = np.linspace(0, 60, 120)
#interpolatedData = processRow(['test.csv', 'test2.csv', 'test3.csv', 'test4.csv'], t)
interpolatedData = processRow(['pipe1', 'pipe2','pipe3','pipe4'], t)

def updateRealtimeVis(quat, idStr, ax):
    if idStr == 'head':
        headPos = quat.rotate([0, 0, 1])
        ind = np.linspace(0,1,11)
        x = [headPos[0]*i for i in ind]
        y = [headPos[1]*i for i in ind]
        z = [headPos[2]*i for i in ind]
        ax.plot(x, y, z)
        return quat

    euler = transformations.euler_from_quaternion([quat[1], quat[2], quat[3], quat[0]])
    print(euler)
    if idStr == 'rightArm':
        ans =  ANGLE_MAP_R[str(rad2Bucket(euler[0]))][str(rad2Bucket(euler[2]))][str(rad2Bucket(euler[1]))]
        if ans['shoulderX'] is not None:
            elbowRelativeEuler = [deg2rad(ans['shoulderX']), deg2rad(ans['shoulderZ']), deg2rad(ans['shoulderY'])]
            elbowRelativeQuat = transformations.quaternion_from_euler(elbowRelativeEuler[0], elbowRelativeEuler[1], elbowRelativeEuler[2])
            elbowRelativeQuat = Quaternion(elbowRelativeQuat[3], elbowRelativeQuat[0], elbowRelativeQuat[1], elbowRelativeQuat[2])
            elbowPos = elbowRelativeQuat.rotate([0, 0, -1])
            wristRelativePos = quat.rotate([0, 0, -1])
            ind = np.linspace(0,1,11)
            x = [0+elbowPos[0]*i for i in ind] + [0+elbowPos[0]+wristRelativePos[0]*i for i in ind]
            y = [-1+elbowPos[1]*i for i in ind] + [-1+elbowPos[1]+wristRelativePos[1]*i for i in ind]
            z = [0+elbowPos[2]*i for i in ind] + [0+elbowPos[2]+wristRelativePos[2]*i for i in ind]
            ax.plot(x, y, z)
            return elbowRelativeQuat
        
    if idStr == 'leftArm':
        #print(euler)
        ans =  ANGLE_MAP_L[str(rad2Bucket(euler[0]))][str(rad2Bucket(euler[2]))][str(rad2Bucket(euler[1]))]
        #print(ans)
        if ans['shoulderX'] is not None:
            elbowRelativeEuler = [deg2rad(ans['shoulderX']), deg2rad(ans['shoulderZ']), deg2rad(ans['shoulderY'])]
            elbowRelativeQuat = transformations.quaternion_from_euler(elbowRelativeEuler[0], elbowRelativeEuler[1], elbowRelativeEuler[2])
            elbowRelativeQuat = Quaternion(elbowRelativeQuat[3], elbowRelativeQuat[0], elbowRelativeQuat[1], elbowRelativeQuat[2])
            elbowPos = elbowRelativeQuat.rotate([0, 0, -1])
            wristRelativePos = quat.rotate([0, 0, -1])
            ind = np.linspace(0,1,11)
            x = [0+elbowPos[0]*i for i in ind] + [0+elbowPos[0]+wristRelativePos[0]*i for i in ind]
            y = [1+elbowPos[1]*i for i in ind] + [1+elbowPos[1]+wristRelativePos[1]*i for i in ind]
            z = [0+elbowPos[2]*i for i in ind] + [0+elbowPos[2]+wristRelativePos[2]*i for i in ind]
            ax.plot(x, y, z)
            return elbowRelativeQuat

def rad2Bucket(rad):
    radInterval = 5*3.1415926/180
    ans = math.floor(rad / radInterval) * 5
    if ans == 180:
        return 180 - 5
    else:
        return ans

def deg2rad(deg): 
  return deg * 3.1415926 / 180

for i in t:
    quatHead, quatLeft, quatRight, _, _, _ = next(interpolatedData)
    #print(quatLeft[0], quatLeft[1], quatLeft[2], quatLeft[3])
    ax.clear()
    ind = np.linspace(0, 1, 11)
    x = [0 for i in ind]
    y = [-1+2*i for i in ind]
    z = [0 for i in ind]
    ax.plot(x, y, z)
    x = [0 for i in ind]
    y = [0 for i in ind]
    z = [-2+2*i for i in ind]
    ax.plot(x, y, z)
    updateRealtimeVis(quatHead, 'head', ax)
    updateRealtimeVis(quatLeft, 'leftArm', ax)
    updateRealtimeVis(quatRight, 'rightArm', ax)
    plt.axis('equal')
    plt.show()
    plt.pause(0.001)

