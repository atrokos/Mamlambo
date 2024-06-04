from functools import total_ordering


@total_ordering
class Group:
    def __init__(self, name):
        self.name = name
        self.parts = name.split("::")

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name
