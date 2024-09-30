class Variable:
    def __init__(self, name, value=1.0, unit=None, description=None):
        """
        Initializes a new instance of the Variable class.

        Args:
            name (str): The name of the variable.
            value (float, optional): The value of the variable. Defaults to 1.0.
            unit (str, optional): The unit of the variable. Defaults to an empty string.
            Description (str, optional): The description of the variable. Defaults to None.
        """
        self.name = name
        self.value = value
        self.unit = unit if unit else ""
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.value} {self.unit}"
