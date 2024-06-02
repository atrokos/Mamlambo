

class Group:
    def __init__(self, name):
        self.name = name
        self.parts = name.split("::")

    def __str__(self):
        return self.name

    def __cmp__(self, other):
        return self.name.__cmp__(other.name)
