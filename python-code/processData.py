from scipy.interpolate import CubicSpline
import tf
import numpy as np
import collections
from pyquaternion import Quaternion

def processRow(data_dirs, t):
    torsoInterpo = createInterpolator(data_dir[0])
    headInterpo = createInterpolator(data_dir[1])
    leftInterpo = createInterpolator(data_dir[2])
    rightInterpo = createInterpolator(data_dir[3])

    torsoQuats = torsoInterpo[6].evaluate(t)
    headQuats = headInterpo[6].evaluate(t)
    leftQuats = leftInterpo[6].evaluate(t)
    rightQuats = rightInterpo[6].evaluate(t)
    torsoAccs = (torsoInterpo[0].evaluate(t), torsoInterpo[1].evaluate(t), torsoInterpo[2].evaluate(t))
    headAccs = (headInterpo[0].evaluate(t), headInterpo[1].evaluate(t), headInterpo[2].evaluate(t))
    leftAccs = (leftInterpo[0].evaluate(t), leftInterpo[1].evaluate(t), leftInterpo[2].evaluate(t))
    rightAccs = (rightInterpo[0].evaluate(t), rightInterpo[1].evaluate(t), rightInterpo[2].evaluate(t))
    

    torsoOffset = Quaternion([1, 0, 0, 0])
    headOffset = Quaternion([1, 0, 0, 0])
    for i in range(0, t):
        torsoQuat = torsoQuats.next()
        torsoQuatValid = torsoQuat[0] is not None and not (torsoQuat[0] == torsoQuat[1] and torsoQuat[0] == torsoQuat[2] and torsoQuat[0] == torsoQuat[3])
        if torsoQuatValid:
            correctedTorsoQuat = torsoQuat*torsoOffset
            torsoAcc = []
            torsoAcc.append(torsoAccs[0].next())
            torsoAcc.append(torsoAccs[1].next())
            torsoAcc.append(torsoAccs[2].next())
            torsoAccMag = np.linalg.norm(torsoAcc)
            if torsoAccMag < threshold:
                torsoOffset = Calibrate(torsoQuat)
        
        headQuat = headQuats.next()
        headQuatValid = headQuat[0] is not None and not (headQuat[0] == headQuat[1] and headQuat[0] == headQuat[2] and headQuat[0] == headQuat[3])
        if headQuatValid:
            correctedHeadQuat = headQuat*headOffset
            headAcc = []
            headAcc.append(headAccs[0].next())
            headAcc.append(headAccs[1].next())
            headAcc.append(headAccs[2].next())
            headAccMag = np.linalg.norm(headAcc)
            if torsoQuatValid:
                headRelativeQuat = correctedTorsoQuat.inverse*correctedHeadQuat
                headRelative = tf.transformations.euler_from_quaternion(headRelativeQuat)
                headAccRelative = [headAcc[i] - torsoAcc[i] for i in range(0, 3)]
                if headAccMag < threshold:
                    headOffset = Calibrate(headQuat)
        
        leftQuat = leftQuats.next()
        leftQuatValid = leftQuat[0] is not None and not (leftQuat[0] == leftQuat[1] and leftQuat[0] == leftQuat[2] and leftQuat[0] == leftQuat[3])
        if leftQuatValid:
            leftAcc.append(leftAccs[0].next())                
            leftAcc.append(leftAccs[1].next())
            leftAcc.append(leftAccs[2].next())
            if torsoQuatValid:
                leftRelativeQuat = correctedTorsoQuat.inverse*leftQuat
                leftRelative = tf.transformations.euler_from_quaternion(leftRelativeQuat)
                leftAccRelative = [leftAcc[i] - torsoAcc[i] for i in range(0, 3)]

        rightQuat = rightQuats.next()
        rightQuatValid = rightQuat[0] is not None and not (rightQuat[0] == rightQuat[1] and rightQuat[0] == rightQuat[2] and rightQuat[0] == rightQuat[3])
        if rightQuatValid:
            rightAcc.append(rightAccs[0].next())
            rightAcc.append(rightAccs[1].next())
            rightAcc.append(rightAccs[2].next())
            if torsoQuatValid:
                rightRelativeQuat = correctedTorsoQuat.inverse*rightQuat
                rightRelative = tf.transformations.euler_from_quaternion(rightRelativeQuat)
                rightAccRelative = [rightAcc[i] - torsoAcc[i] for i in range(0, 3)]
        yield (headRelative, leftRelative, rightRelative, headAccRelative, leftAccRelative, rightAccRelative)



def readData(ind, data_dir):
    f = open(data_dir, 'r')
    line = f.readline()
    while line:
        linelist = line.split(' ')
        for i in ind:
            result.append(float(linelist[i]))
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
        time0, data0 = self.data_time.next()
        time1, data1 = self.data_time.next()
        q = []
        for i in range(0, len(t)):
            try:
                while t[i] > time1:
                    time0 = time1
                    data0 = data1
                    time1, data1 = self.data_time.next()
            except e:
                continue
            q0 = tf.transformations.quaternion_from_euler(data0[0], data0[1], data0[2]) 
            q1 = tf.transformations.quaternion_from_euler(data1[0], data1[1], data1[2])
            q0 = Quaternion(q0)
            q1 = Quaternion(q1)

            w = (t[i] - t1)/(t2 - t1)
            yield Quaternion.slerp(q0, q1, w)

class InterpoCubic:
    def __init__(self, data_time):
        self.data_time = data_time

    def evaluate(self, t):
        qtime = collection.deque([])
        qdata = collection.deque([])
        for i in range(0, 11):
            time, data = next(data_time)
            qtime.append(time)
            qdata.append(data)
        for i in range(0, len(t)):
            while t[i] > qtime[5]:
                time, data = next(data_time)
                qtime.append(time)
                qdata.append(data)
                qtime.popleft()
                qdata.popleft()
            poly = CubicSpline(qtime, qdata)
            yield poly(t)

def Calibrate(quat):
    torsoZRotate = Quaternion([0.707, 0, 0, 0.707])
    offset = quat*torso
    euler = tf.transformations.euler_from_quaternion(offset)
    euler[0] = 0
    euler[2] = 0
    expected = tf.transformations.quaternion_from_euler(euler)
    expected = Quaternion(expected)
    Offset =quat.inverse*expected

