import cv2
from matplotlib import pyplot
import numpy as np


def read_sample(filenames):
    images = []

    for filename in filenames:
        image = cv2.imread(filename)
        image = cv2.resize(image, (96, 96))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_array = []

        for y in range(0, 96, 1):
            for x in range(0, 96, 1):
                image_array.append((image[y][x] / 255.))

        image_array = np.array(image_array)
        image_array = image_array.astype(np.float32)

        images.append(image_array)

    return np.vstack(images)


def plot_sample(x, y, axis):
    img = x.reshape(96, 96)
    axis.imshow(img, cmap='gray')
    axis.scatter(y[0::2] * 48 + 48, y[1::2] * 48 + 48, marker='x', s=10)


def draw_result(X, y):
    fig = pyplot.figure(figsize=(6, 6))
    fig.subplots_adjust(
        left=0, right=1, bottom=0, top=1, hspace=0.05, wspace=0.05)

    for i in range(X.shape[0]):
        ax = fig.add_subplot(4, 4, i + 1, xticks=[], yticks=[])
        plot_sample(X[i], y[i], ax)

    pyplot.show()