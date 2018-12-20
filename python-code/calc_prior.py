from processData import readData, InterpoQuat
import subprocess
import transformations

wrist_file_name = 'leftWrist.csv'
elbow_file_name = 'leftElbow.csv'
torso_file_name = 'torso.csv'
bucketSize = 5

f = open('leftPrior', 'w')
w = readData([0, 1, 2], wrist_file_name)
e = readData([0, 1, 2], elbow_file_name)
t = readData([0, 1, 2], torso_file_name)
tail = subprocess.run('tail '+wrist_file_name, stdout=subprocess.PIPE, shell=True)
tail = tail.stdout.decode('utf-8')
lastline = tail.split('\n')[-2]
max_time = lastline.split(', ')[-1]
t = np.linspace(5, max_time, (max_time-5)*50)
wristQuats = InterpoQuat(w).evaluate(t)
elbowQuats = InterpoQuat(e).evaluate(t)
torsoQuats = InterpoQuat(t).evaluate(t)

prior = {}
for i in t:
    torsoQuat = next(torsoQuats)
    wristQuat = next(wristQuats)
    elbowQuat = next(elbowQuats)
    wristRelativeQuat = torsoQuat.inverse*wristQuat
    elbowRelativeQuat = elbowQuat.inverse*elbowQuat
    wristEuler = transformations.euler_from_quaternion([wristRelativeQuat[1], wristRelativeQuat[2], wristRelativeQuat[3], wristRelativeQuat[0]])
    elbowEuler = transformations.euler_from_quaternion([elbowRelativeQuat[1], elbowRelativeQuat[2], elbowRelativeQuat[3], elbowRelativeQuat[0]])
    prior[str(rad2Bucket(wristEuler[0]))+' '+str(rad2Bucket(wristEuler[1]))+' '+str(rad2Bucket(wristEuler[2]))][str(rad2Bucket(elbowEuler[0]))+' '+str(rad2Bucket(elbowEuler[1]))+' '+str(rad2Bucket(elbowEuler[2]))] += 1

json.dump(prior, f)
f.close()

def rad2Bucket(rad):
    radInterval = bucketSize*3.1415926/180
    ans = math.floor(rad / radInterval) * bucketSize
    if ans == 180:
        return 180 - bucketSize
    else:
        return ans

def deg2rad(deg):
  return deg * 3.1415926 / 180
