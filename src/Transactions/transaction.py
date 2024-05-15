import sqlite3
from datetime import date


class Transaction:
    converters = [int, date]
    def __init__(self, tid: int, tdate: date, title: str, group, amount, currency, note):
        self._tid = tid
        self._date = tdate
        self._title = title
        self._group = group
        self._amount = amount
        self._currency = currency
        self._note = note

    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return \
            f"{self._tid};{self._date};{self._title};{self._group};{self._amount};{self._currency};{self._note}"

    @staticmethod
    def convert(sql_item):


    @property
    def date(self):
        return self._date

    @property
    def title(self):
        return self._title

    @property
    def group(self):
        return self._group

    @property
    def amount(self):
        return self._amount

    @property
    def currency(self):
        return self._currency

    @property
    def description(self):
        return self._note
