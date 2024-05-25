


class Group:
    def __init__(self, name):
        self.name = name.split("::")

    def __str__(self):
        return "::".join(self.name)
