import csv
import numpy as np
import json

def getParameters():
    """" Extracting the parameters from the InputParameters file """

    with open('InputParameters.json') as jsonFile:
        data = json.load(jsonFile)

    return data


def createNewLogFile():
    f = open("Log.txt", "w")
    f.close()


def logIntoFile(string):
    f = open("Log.txt", "a")
    f.write(string)
    f.close()


def openState(stateNumber):
    """" Returning the state data as numpy array """

    with open('Data/State/state' + str(stateNumber) + '.csv') as f:
        reader = csv.reader(f)
        data = list(reader)

    return np.asarray(data, dtype=np.float32)


def logIfDetectMotion(frameNumber, trolleyMoved, jibMoved, hookMoved):
    """" Log into file if motion has detected in any of the parts """

    if trolleyMoved:
        logIntoFile("Frame No." + str(frameNumber) + " - Trolley Moved\n")
    if jibMoved:
        logIntoFile("Frame No." + str(frameNumber) + " - Jib Moved\n")
    if hookMoved:
        logIntoFile("Frame No." + str(frameNumber) + " - Hook Moved\n")