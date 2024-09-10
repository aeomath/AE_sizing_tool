class Variable:
    def __init__(self, name, value=1.0, unit=None):
        self.name = name
        self.value = value
        self.unit = unit if unit else ""

    def __str__(self):
        return f"{self.name}: {self.value} {self.unit}"
