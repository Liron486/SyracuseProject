from PointCloudHandler import PointCloudHandler
import Utils
import numpy as np


def mainFunction():
    """"
    The main function of the program - Creates an instance of PointCloudHandler
    and analyze the frames according to the parameters in the InputParamers file.

    Parameters:
        First Frame - The first frame we want to analyze.
        Last Frame - The last frame we want to analyze.
        MinX/MaxX - The minimum and the maximum values acceptable in the X axis (the same for the Y and Z axis).
        Closeness - Value to pass to clustering method to filter points that are to close to each other.
        View Point - The angle we want to watch the point cloud image. The options are: Front, Back, Left, Right, Top.
        Trolley Threshold - If the trolley velocity exceeds that value the frame will be disqualified.
        Jib Threshold - If the jib velocity exceeds that value the frame will be disqualified.
        Hook Threshold - If the hook velocity exceeds that value the frame will be disqualified.
        Time Between Frames - The time that passing between two frames.
        Batch Size - The amount of frames that we want to analyze together.
        Slicing - Indicates if we want to slice our data.
        Clustering - Indicates if we want to cluster our data.
        Inspection - Indicates if we want to display our data.

    """
    Utils.createNewLogFile()
    data = Utils.getParameters()
    pcHandler = PointCloudHandler(data["MinX"], data["MaxX"], data["MinY"], data["MaxY"], data["MinZ"], data["MaxZ"],
                                  data["Closeness"], data["Trolley Threshold"], data["Jib Threshold"],
                                  data["Hook Threshold"], data["Time Between Frames"])

    for i in range(data["First Frame"], data["Last Frame"], data["Batch Size"]):
        pc = np.array([], dtype=np.float32).reshape(0, 3)

        if data["Clustering"]:
            pc = pcHandler.clustering(i, i + data["Batch Size"])

        if data["Slicing"]:
            if pc.size == 0 and not data["Clustering"]:
                pc = pcHandler.slicing(i, i + data["Batch Size"])
            else:
                pc = pcHandler.slicing(pc)

        if data["Inspection"]:
            if pc.size == 0 and not data["Slicing"] and not data["Clustering"]:
                pcHandler.inspection(i, i + data["Batch Size"], data["View Point"])
            else:
                pcHandler.inspection(pc, data["View Point"])


if __name__ == '__main__':
    mainFunction()
