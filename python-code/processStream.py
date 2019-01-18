#euler_order: roll, pitch, yaw
#original euler_order: yaw pitch roll
#euler_order in oriTrakHAR: roll yaw pitch

from scipy.interpolate import CubicSpline
import transformations
import numpy as np
import collections
import os
import time
import threading
import queue
from pyquaternion import Quaternion
threshold = 1

def display(quat):
    print(quat[0], quat[1], quat[2], quat[3])

def processRow(data_dirs, t):
    torsoInterpo = createInterpolator(data_dirs[0])
    headInterpo = createInterpolator(data_dirs[1])
    leftInterpo = createInterpolator(data_dirs[2])
    rightInterpo = createInterpolator(data_dirs[3])

    torsoQuats = torsoInterpo[3].evaluate(t)
    headQuats = headInterpo[3].evaluate(t)
    leftQuats = leftInterpo[3].evaluate(t)
    rightQuats = rightInterpo[3].evaluate(t)
    torsoAccs = (torsoInterpo[0].evaluate(t), torsoInterpo[1].evaluate(t), torsoInterpo[2].evaluate(t))
    headAccs = (headInterpo[0].evaluate(t), headInterpo[1].evaluate(t), headInterpo[2].evaluate(t))
    leftAccs = (leftInterpo[0].evaluate(t), leftInterpo[1].evaluate(t), leftInterpo[2].evaluate(t))
    rightAccs = (rightInterpo[0].evaluate(t), rightInterpo[1].evaluate(t), rightInterpo[2].evaluate(t))
    

    #torsoOffset = Quaternion([-0.01483, 0.659224, 0.747234, 0.082578])
    #headOffset = Quaternion([-0.101687, 0.62569, 0.77248, 0.038392])
    torsoOffset = Quaternion([1, 0, 0, 0])
    headOffset = Quaternion([1, 0, 0, 0])
    for i in t:
        torsoQuat = next(torsoQuats)
        #print(torsoQuat[0], torsoQuat[1], torsoQuat[2], torsoQuat[3])
        torsoQuatValid = torsoQuat[0] is not None and not (torsoQuat[0] == torsoQuat[1] and torsoQuat[0] == torsoQuat[2] and torsoQuat[0] == torsoQuat[3])
        if torsoQuatValid:
            correctedTorsoQuat = torsoQuat*torsoOffset
            #display(correctedTorsoQuat)
            torsoAcc = []
            torsoAcc.append(next(torsoAccs[0]))
            torsoAcc.append(next(torsoAccs[1]))
            torsoAcc.append(next(torsoAccs[2]))
            torsoAccMag = np.linalg.norm(torsoAcc)
            if torsoAccMag < threshold:
                torsoOffset = Calibrate(torsoQuat)
                #print(torsoOffset)
        
        headQuat = next(headQuats)
        headQuatValid = headQuat[0] is not None and not (headQuat[0] == headQuat[1] and headQuat[0] == headQuat[2] and headQuat[0] == headQuat[3])
        if headQuatValid:
            correctedHeadQuat = headQuat*headOffset
            headAcc = []
            headAcc.append(next(headAccs[0]))
            headAcc.append(next(headAccs[1]))
            headAcc.append(next(headAccs[2]))
            headAccMag = np.linalg.norm(headAcc)
            if torsoQuatValid:
                headRelativeQuat = correctedTorsoQuat.inverse*correctedHeadQuat
                #headRelative = transformations.euler_from_quaternion(headRelativeQuat)
                headAccRelative = [headAcc[i] - torsoAcc[i] for i in range(0, 3)]
                if headAccMag < threshold:
                    headOffset = Calibrate(headQuat)
                    #print(headOffset)
        leftQuat = next(leftQuats)
        leftQuatValid = leftQuat[0] is not None and not (leftQuat[0] == leftQuat[1] and leftQuat[0] == leftQuat[2] and leftQuat[0] == leftQuat[3])
        if leftQuatValid:
            leftAcc = []
            leftAcc.append(next(leftAccs[0]))                
            leftAcc.append(next(leftAccs[1]))
            leftAcc.append(next(leftAccs[2]))
            if torsoQuatValid:
                leftRelativeQuat = correctedTorsoQuat.inverse*leftQuat
                #leftRelative = transformations.euler_from_quaternion(leftRelativeQuat)
                #display(leftQuat)
                leftAccRelative = [leftAcc[i] - torsoAcc[i] for i in range(0, 3)]

        rightQuat = next(rightQuats)
        rightQuatValid = rightQuat[0] is not None and not (rightQuat[0] == rightQuat[1] and rightQuat[0] == rightQuat[2] and rightQuat[0] == rightQuat[3])
        if rightQuatValid:
            rightAcc = []
            rightAcc.append(next(rightAccs[0]))
            rightAcc.append(next(rightAccs[1]))
            rightAcc.append(next(rightAccs[2]))
            if torsoQuatValid:
                rightRelativeQuat = correctedTorsoQuat.inverse*rightQuat
                #rightRelative = transformations.euler_from_quaternion(rightRelativeQuat)
                rightAccRelative = [rightAcc[i] - torsoAcc[i] for i in range(0, 3)]
        yield (headRelativeQuat, leftRelativeQuat, rightRelativeQuat, headAccRelative, leftAccRelative, rightAccRelative)



def readData(inds, queues, data_dir):
    f = os.open(data_dir, os.O_NONBLOCK)
    while True:
        try:
            line = os.read(f, 4096).decode()
            if len(line) > 0:
                line = line.split('\n')[-2]
                linelist = line.split(',')
                t = float(linelist[0])
                for i, ind in enumerate(inds):
                    result = []
                    for j in ind:
                        result.append(float(linelist[j]))
                    queues[i].put((t, result))
            else:
                time.sleep(0.05)
        except OSError as err:
            if err.errno == 11:
                continue
            else:
                raise err
        


def createInterpolator(data_dir):
    queues = [queue.Queue() for i in [0, 1, 2, 3]]
    th = threading.Thread(target=readData, args=([[3], [4], [5], [12, 13, 14]], queues, data_dir))
    th.daemon = True
    th.start()
    acc_x_inter = InterpoCubic(queues[0])
    acc_y_inter = InterpoCubic(queues[1])
    acc_z_inter = InterpoCubic(queues[2])
    quat_inter = InterpoQuat(queues[3])

    return (acc_x_inter, acc_y_inter, acc_z_inter, quat_inter)


class InterpoQuat:
    def __init__(self, data_time):
        self.data_time = data_time

    def evaluate(self, t):
        t0, data0 = self.data_time.get(block=True)
        t1, data1 = self.data_time.get(block=True)
        q = []
        for i in range(0, len(t)):
            while t[i] > t1:
                t0 = t1
                data0 = data1
                t1, data1 = self.data_time.get(block=True)

            #Here I assumed roll pitch yaw, but data may come in a different order
            q0 = transformations.quaternion_from_euler(data0[0], data0[1], data0[2]) 
            q1 = transformations.quaternion_from_euler(data1[0], data1[1], data1[2])
            q0 = Quaternion(q0[3], q0[0], q0[1], q0[2])
            q1 = Quaternion(q1[3], q1[0], q1[1], q1[2])

            w = (t[i] - t0)/(t1 - t0)
            yield Quaternion.slerp(q0, q1, w)

class InterpoCubic:
    def __init__(self, data_time):
        self.data_time = data_time

    def evaluate(self, t):
        qtime = collections.deque([])
        qdata = collections.deque([])
        for i in range(0, 11):
            time, data = self.data_time.get(block=True)
            qtime.append(time)
            qdata.append(data)
        for i in range(0, len(t)):
            while t[i] > qtime[5]:
                time, data = self.data_time.get(block=True)
                qtime.append(time)
                qdata.append(data)
                qtime.popleft()
                qdata.popleft()
            poly = CubicSpline(qtime, qdata)
            yield poly(t)

def Calibrate(quat):
    #torsoZRotate = Quaternion([0.707, 0, 0, 0.707])
    torsoZRotate = Quaternion([1, 0, 0, 0])
    offset = quat*torsoZRotate
    euler = list(transformations.euler_from_quaternion([offset[1], offset[2], offset[3], offset[0]]))
    euler[0] = 0  #roll
    euler[1] = 0  #pitch
    expected = transformations.quaternion_from_euler(euler[0], euler[1], euler[2])
    expected = Quaternion(expected[3], expected[0], expected[1], expected[2])
    Offset = quat.inverse*expected
    return Offset

