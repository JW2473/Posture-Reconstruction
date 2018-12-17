#euler_order: roll, pitch, yaw
#original euler_order: yaw pitch roll
#euler_order in oriTrakHAR: roll yaw pitch

from scipy.interpolate import CubicSpline
import transformations
import numpy as np
import collections
from pyquaternion import Quaternion
threshold = 1

def processRow(data_dirs, t):
    torsoInterpo = createInterpolator(data_dirs[0])
    headInterpo = createInterpolator(data_dirs[1])
    leftInterpo = createInterpolator(data_dirs[2])
    rightInterpo = createInterpolator(data_dirs[3])

    torsoQuats = torsoInterpo[6].evaluate(t)
    headQuats = headInterpo[6].evaluate(t)
    leftQuats = leftInterpo[6].evaluate(t)
    rightQuats = rightInterpo[6].evaluate(t)
    torsoAccs = (torsoInterpo[0].evaluate(t), torsoInterpo[1].evaluate(t), torsoInterpo[2].evaluate(t))
    headAccs = (headInterpo[0].evaluate(t), headInterpo[1].evaluate(t), headInterpo[2].evaluate(t))
    leftAccs = (leftInterpo[0].evaluate(t), leftInterpo[1].evaluate(t), leftInterpo[2].evaluate(t))
    rightAccs = (rightInterpo[0].evaluate(t), rightInterpo[1].evaluate(t), rightInterpo[2].evaluate(t))
    

    #torsoOffset = Quaternion([-0.01483, 0.659224, 0.747234, 0.082578])
    #headOffset = Quaternion([-0.101687, 0.62569, 0.77248, 0.038392])
    torsoOffset = Quaternion([1, 0, 0, 0])
    headOffset = Quaternion([1, 0, 0, 0])
    for i in range(0, len(t)):
        torsoQuat = next(torsoQuats)
        torsoQuatValid = torsoQuat[0] is not None and not (torsoQuat[0] == torsoQuat[1] and torsoQuat[0] == torsoQuat[2] and torsoQuat[0] == torsoQuat[3])
        if torsoQuatValid:
            correctedTorsoQuat = torsoQuat*torsoOffset
            torsoAcc = []
            torsoAcc.append(next(torsoAccs[0]))
            torsoAcc.append(next(torsoAccs[1]))
            torsoAcc.append(next(torsoAccs[2]))
            torsoAccMag = np.linalg.norm(torsoAcc)
            if torsoAccMag < threshold:
                torsoOffset = Calibrate(torsoQuat)
        
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



def readData(ind, data_dir):
    f = open(data_dir, 'r')
    line = f.readline()
    while line:
        linelist = line.split(', ')
        result = []
        for i in ind:
            result.append(float(linelist[i]))
        line = f.readline()
        yield float(linelist[9]), result

def createInterpolator(data_dir):
    gyro_x_data = readData([6], data_dir)
    gyro_y_data = readData([7], data_dir)
    gyro_z_data = readData([8], data_dir)
    acc_x_data = readData([3], data_dir)
    acc_y_data = readData([4], data_dir)
    acc_z_data = readData([5], data_dir)
    euler_data = readData([0, 1, 2], data_dir)

    gyro_x_inter = InterpoCubic(gyro_x_data)
    gyro_y_inter = InterpoCubic(gyro_y_data)
    gyro_z_inter = InterpoCubic(gyro_z_data)
    acc_x_inter = InterpoCubic(acc_x_data)
    acc_y_inter = InterpoCubic(acc_y_data)
    acc_z_inter = InterpoCubic(acc_z_data)
    quat_inter = InterpoQuat(euler_data)
    return (acc_x_inter, acc_y_inter, acc_z_inter, gyro_x_inter, gyro_y_inter, gyro_z_inter, quat_inter)


class InterpoQuat:
    def __init__(self, data_time):
        self.data_time = data_time

    def evaluate(self, t):
        t0, data0 = next(self.data_time)
        t1, data1 = next(self.data_time)
        q = []
        for i in range(0, len(t)):
            while t[i] > t1:
                t0 = t1
                data0 = data1
                t1, data1 = next(self.data_time)
            q0 = transformations.quaternion_from_euler(data0[0], data0[1], data0[2]) 
            q1 = transformations.quaternion_from_euler(data1[0], data1[1], data1[2])
            q0 = Quaternion(q0)
            q1 = Quaternion(q1)

            w = (t[i] - t0)/(t1 - t0)
            yield Quaternion.slerp(q0, q1, w)

class InterpoCubic:
    def __init__(self, data_time):
        self.data_time = data_time

    def evaluate(self, t):
        qtime = collections.deque([])
        qdata = collections.deque([])
        for i in range(0, 11):
            time, data = next(self.data_time)
            qtime.append(time)
            qdata.append(data)
        for i in range(0, len(t)):
            while t[i] > qtime[5]:
                time, data = next(self.data_time)
                qtime.append(time)
                qdata.append(data)
                qtime.popleft()
                qdata.popleft()
            poly = CubicSpline(qtime, qdata)
            yield poly(t)

def Calibrate(quat):
    torsoZRotate = Quaternion([0.707, 0, 0, 0.707])
    offset = quat*torsoZRotate
    euler = list(transformations.euler_from_quaternion([offset[0], offset[1], offset[2], offset[3]]))
    euler[0] = 0  #roll
    euler[1] = 0  #pitch
    expected = transformations.quaternion_from_euler(euler[0], euler[1], euler[2])
    expected = Quaternion(expected)
    Offset =quat.inverse*expected

