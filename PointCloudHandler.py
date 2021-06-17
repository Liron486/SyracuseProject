import csv
import numpy as np
import rtree
import matplotlib.pyplot as plt
from pathlib import Path
from StateHandler import StateHandler
import Utils


def getFramesAsArray(stateHandler, startFrame, endFrame):
    """
        Extracting range of frames data into numpy array,
        excluding frames that one of the crane's parts move too fast.

    :param stateHandler: Instance of StateHandler to check if the velocity exceeds the thresholds.
    :param startFrame: The first frame we want to extract.
    :param endFrame: The last frame we want to extract.
    :return: numpy array of all the data between startFrame and endFrame, excluding disqualified frames.
    """
    arr = np.array([], dtype=np.float32).reshape(0, 3)

    for i in range(startFrame, endFrame):
        file = Path('Data/PC/frame' + str(i) + '.csv')
        if file.is_file():
            with open('Data/PC/frame' + str(i) + '.csv') as f:
                reader = csv.reader(f)
                data = list(reader)
                newArr = np.asarray(data, dtype=np.float32)

                motion = stateHandler.motionDetection(i)
                Utils.logIfDetectMotion(i, *motion)
                velocities = stateHandler.motionVelocity(*motion)

                if True not in velocities["TooFast"].values():
                    arr = np.vstack((arr, newArr))

    return arr, stateHandler


class PointCloudHandler:
    """
        Class to handle point could data
    """
    def __init__(self, minX, maxX, minY, maxY, minZ, maxZ, closeness, trolleyThreshold, jibThreshold, hookThreshold,
                 timeBetweenFrames):
        self.x = [minX, maxX]
        self.y = [minY, maxY]
        self.z = [minZ, maxZ]
        self.closeness = closeness
        self.stateHandler = StateHandler(trolleyThreshold, jibThreshold, hookThreshold, timeBetweenFrames)

    def slicing(self, *args):
        """
            Slicing the point could data according to the XYZ axis.

        The function can get range of numbers to read the point cloud data from the frames,
        or it can get a numpy array with the data.

        BE AWARE - reading a frame more than once will lead to undefined behavior,
        after using slicing or clustering you have to use their output.

        :return: numpy array with the sliced data.
        """
        if len(args) == 2:
            pc, self.stateHandler = getFramesAsArray(self.stateHandler, args[0], args[1])
        else:
            pc = args[0]

        lineCounter = 0

        for p in pc:
            if not self.__contains(p):
                pc = np.delete(pc, lineCounter, axis=0)
            else:
                lineCounter += 1

        return pc

    def clustering(self, *args):
        """
            Removing points that are too close to each other (less than closeness parameter)

        The function can get range of numbers to read the point cloud data from the frames,
        or it can get a numpy array with the data.

        BE AWARE - reading a frame more than once will lead to undefined behavior,
        after using slicing or clustering you have to use their output.

        :return: numpy array with the filtered data.
        """

        if len(args) == 2:
            pc, self.stateHandler = getFramesAsArray(self.stateHandler, args[0], args[1])
        else:
            pc = args[0]

        result = []
        prop = rtree.index.Property()
        prop.dimension = 3
        index = rtree.index.Index(properties=prop)

        for i, p in enumerate(pc):
            px, py, pz = p
            r = self.closeness
            nearby = index.intersection((px - r, py - r, pz - r, px + r, py + r, pz + r))

            if all(np.linalg.norm(p - pc[j]) >= r for j in nearby):
                result.append(p)
                index.insert(i, (px, py, pz, px, py, pz))

        return np.array(result)

    def inspection(self, *args):
        """
            Displays point cloud data

        The function can get range of numbers to read the point cloud data from the frames,
        or it can get a numpy array with the data.
        And also it needs a view point in which you want to see the figure.
        The options are: Front, Right, Left, Back, Top.

        BE AWARE - reading a frame more than once will lead to undefined behavior,
        after using slicing or clustering you have to use their output.

        """
        if len(args) == 3:
            pc, self.stateHandler = getFramesAsArray(self.stateHandler, args[0], args[1])
            view = args[2]
        else:
            pc = args[0]
            view = args[1]

        rgb = [1] * (pc.size // 3)
        viewDict = {"Top": [90, 0], "Front": [30, 45], "Left": [30, 315], "Back": [30, 225], "Right": [30, 135]}

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(*viewDict[view])
        if pc.size != 0:
            ax.scatter(pc[:, 0], pc[:, 1], pc[:, 2], c=rgb, s=0.1)

        plt.show(block=False)
        plt.pause(0.1)
        plt.close()

    def __contains(self, point):
        """
            Checks if a point is inside a cuboid

        :param point: numpy array representing a point in 3D
        :return: True if the point is inside the cuboid or False otherwise.
        """
        px = self.x[0] <= point[0] <= self.x[1]
        py = self.y[0] <= point[1] <= self.y[1]
        pz = self.z[0] <= point[2] <= self.z[1]

        return px and py and pz
