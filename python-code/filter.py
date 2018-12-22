import numpy as np
from processStream import processRow

dt = 0.05
sigma = 0.1
t = np.linspace(0, 100, 100/dt)

interpolatedData = processRow(['pipe1', 'pipe2','pipe3','pipe4'], t)
_, leftQuat2, rightQuat2, _, _, _ = next(interpolatedData)
leftPoswe2 = leftQuat2.rotate([0, 0, -1])
rightPoswe2 = rightQuat2.rotate([0, 0, -1])
_, leftQuat1, rightQuat1, _, _, _ = next(interpolatedData)
leftPoswe1 = leftQuat1.rotate([0, 0, -1])
rightPoswe1 = rightQuat1.rotate([0, 0, -1])

_, leftQuat, rightQuat, _, leftAcc, rightAcc = next(interpolatedData)
leftPoswe = leftQuat.rotate([0, 0, -1])
rightPoswe = rightQuat.rotate([0, 0, -1])
leftAccwe = (leftPoswe + leftPoswe2 - 2*leftPoswe1)/dt**2
rightAccwe = (rightPoswe + rightPoswe2 - 2*rightPoswe1)/dt**2
leftAccElbow = leftQuat.rotate(leftAcc) - leftAccwe
rightAccElbow = rightQuat.rotate(rightAcc) - rightAccwe

def gaussian1D(sigma):
    x = np.linspace(-0.5, 0.51, 11)
    density = np.exp(np.square(x)/sigma)
    return density

def gaussian3D(u, sigma):
    x = np.linspace(-1, 1.01, 21) - u[0]
    y = np.linspace(-1, 1.01, 21) - u[1]
    z = np.linspace(-1, 1.01, 21) - u[2]
    xv, yv, zv = np.meshgrid(x, y, z)
    xv = np.expand_dims(xv, axis=-1)
    yv = np.expand_dims(xv, axis=-1)
    zv = np.expand_dims(xv, axis=-1)
    cat = np.concatenate(xv, yv, zv, axis=-1)
    density  = np.exp(np.sum(np.matmul(cat, sigma)*cat, axis=-1))
    return density

def next(p1, p2, prior, acc):
    density = 2*p1 - p2 + t**2*acc
    kernel = gaussian1D(sigma)
    np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='full'), axis=0, arr=density)
    np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='full'), axis=1, arr=density)
    np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='full'), axis=2, arr=density)
    return density*prior

