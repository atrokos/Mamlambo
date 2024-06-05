from enum import Enum


# Represents an ordering, ascending or descending
class Order(Enum):
    ASC = 0
    DESC = 1


# Lists the properties of a transaction
class Property(Enum):
    DATE = 0
    TITLE = 1
    GROUP = 2
    AMOUNT = 3
    CURRENCY = 4


# Lists various database actions
class Action(Enum):
    NONE = 0  # No action was performed
    LOAD = 1  # Database was loaded
    PUSH = 2  # Pushing changes (i.e. calling add, remove, edit)
    STATE_CHANGE = 3  # Commiting / reverting changes
