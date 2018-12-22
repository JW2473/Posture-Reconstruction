import numpy as np

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
    t = 0.02
    sigma = 0.5
    density = 2*p1 - p2 + t^2*acc
    kernel = gaussian1D(sigma)
    np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='full'), axis=0, arr=density)
    np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='full'), axis=1, arr=density)
    np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='full'), axis=2, arr=density)
    return density*prior

