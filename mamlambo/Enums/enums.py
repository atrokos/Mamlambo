from enum import Enum


class Order(Enum):
    ASC = 0
    DESC = 1


class Property(Enum):
    DATE = 0
    TITLE = 1
    GROUP = 2
    AMOUNT = 3
    CURRENCY = 4


class Action(Enum):
    NONE = 0  # No action was performed
    LOAD = 1  # Database was loaded
    PUSH = 2  # Pushing changes (i.e. calling add, remove, edit)
    STATE_CHANGE = 3  # Commiting / reverting changes
