import Utils


class StateHandler:
    """
        This class is handling state data
    """
    def __init__(self, trolleyThreshold, jibThreshold, hookThreshold, timeBetweenFrames):
        self.speedThresholds = {"Trolley": trolleyThreshold, "Jib": jibThreshold, "Hook": hookThreshold}
        self.locations = {"Trolley": -1, "Jib": -1, "Hook": -1}
        self.movements = {"Trolley": 0, "Jib": 0, "Hook": 0}
        self.timeBetweenFrames = timeBetweenFrames
        self.beforeFirstState = True

    def motionDetection(self, stateNumber):
        """
            check if there is a motion in any of the crane's parts.
            for the first analyzed state no motion will be detect

        :param stateNumber: The state in which we want to detect motion
        :return: List of boolean values at this order: Trolley, Jib, Hook.
        """
        state = Utils.openState(stateNumber)[0]
        result = [False, False, False]

        if not self.beforeFirstState:
            self.movements["Trolley"] = abs(state[0] - self.locations["Trolley"])
            self.movements["Jib"] = abs(state[1] - self.locations["Jib"])
            self.movements["Hook"] = abs(state[2] - self.locations["Hook"])
            result[0] = self.movements["Trolley"] > 0.001
            result[1] = self.movements["Jib"] > 0.001
            result[2] = self.movements["Hook"] > 0.001

        self.locations["Trolley"] = state[0]
        self.locations["Jib"] = state[1]
        self.locations["Hook"] = state[2]
        self.beforeFirstState = False

        return result

    def motionVelocity(self, trolleyMoved, jibMoved, hookMoved):
        """
            Calculate the velocity of the crane's parts and check if one of them is moving too fast.

        :param trolleyMoved: True is motion has detected in trolley, False otherwise.
        :param jibMoved: True is motion has detected in jib, False otherwise.
        :param hookMoved: True is motion has detected in hook, False otherwise.
        :return: List of the velocities of the parts in that order: Trolley, Jib, Hook.
        """
        velocities = {"Values": {"Trolley": 0, "Jib": 0, "Hook": 0},
                      "TooFast": {"Trolley": False, "Jib": False, "Hook": False}}

        if trolleyMoved:
            velocities["Values"]["Trolley"] = self.movements["Trolley"] / self.timeBetweenFrames

        if jibMoved:
            velocities["Values"]["Jib"] = self.movements["Jib"] / self.timeBetweenFrames

        if hookMoved:
            velocities["Values"]["Hook"] = self.movements["Hook"] / self.timeBetweenFrames

        if velocities["Values"]["Trolley"] > self.speedThresholds["Trolley"]:
            velocities["TooFast"]["Trolley"] = True
            alert = "Trolley is too fast!\nSpeed: " + str(
                velocities["Values"]["Trolley"]) + "\n"
            Utils.logIntoFile(alert)
            print(alert)

        if velocities["Values"]["Jib"] > self.speedThresholds["Jib"]:
            velocities["TooFast"]["Jib"] = True
            alert = "Jib is too fast!\nSpeed: " + str(velocities["Values"]["Jib"]) + "\n"
            Utils.logIntoFile(alert)
            print(alert)

        if velocities["Values"]["Hook"] > self.speedThresholds["Hook"]:
            velocities["TooFast"]["Hook"] = True
            alert = "Hook is too fast!\nSpeed: " + str(velocities["Values"]["Hook"]) + "\n"
            Utils.logIntoFile(alert)
            print(alert)

        return velocities
