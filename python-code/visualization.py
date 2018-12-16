import math

def updateRealtimeVis(euler, idStr):
    if idStr == 'head':
        return quat
        #to be done
    if idStr == 'rightArm':
        ans =  ANGLE_MAP_R[rad2Bucket(euler[0])][rad2Bucket(euler[1])][rad2Bucket(euler[2])]
        if ans.shoulderX is not None:
            elbowRelativeEuler = [deg2rad(ans.shoulderX), deg2rad(ans.shoulderY), deg2rad(ans.shoulderZ)]
            return elbowRelativeEuler
        #to be done
    if idStr = 'leftArm':
        ans =  ANGLE_MAP_R[rad2Bucket(euler[0])][rad2Bucket(euler[1])][rad2Bucket(euler[2])]
        if ans.shoulderX is not None:
            elbowRelativeEuler = [deg2rad(ans.shoulderX), deg2rad(ans.shoulderY), deg2rad(ans.shoulderZ)]
            return elbowRelativeEuler
        #to be done

def rad2Bucket(rad):
    radInterval = 5*3.1415926/180
    ans = math.floor(rad / radInterval) * 5
    if ans == 180:
        return 180 - 5
    else:
        return ans
