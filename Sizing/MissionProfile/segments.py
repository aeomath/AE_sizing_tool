from abc import abstractmethod
from Sizing.Variable_info.Variable import Variable


class segments:
    def __init__(self, type, phase_number, weight_fraction=1, name=None):
        self.type = type
        self.phase_number = phase_number
        self.weight_fraction = Variable(
            "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
        )  # Weight fraction (beta)
        if name is None:
            self.name = type + "Phase number" + str(phase_number)
        else:
            self.name = name

    @abstractmethod
    def wf_wi(self, wing_loading, TWR):
        print("error, this method should be implemented in the subclass")
        return 1

    def __str__(self):
        return "Segment type: " + self.type + "\n" " Phase number: \n " + str(
            self.phase_number
        )

    @abstractmethod
    def Thrust_Weight_Ratio(self, WSR):
        print("error, this method should be implemented in the subclass")
        pass

    def __repr__(self):
        return f"Segment(name={self.name!r}, weight_fraction={self.weight_fraction!r}, attributes={self.__dict__!r})"

    def __eq__(self, other):
        if not isinstance(other, segments):
            return False
        return (
            self.type == other.type
            and self.phase_number == other.phase_number
            and self.weight_fraction == other.weight_fraction
        )
