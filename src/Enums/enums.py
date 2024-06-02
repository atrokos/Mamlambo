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
