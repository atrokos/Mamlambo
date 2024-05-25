from datetime import date
from src.Transactions.group import Group


class Transaction:
    def __init__(self, tid: int, tdate: date, title: str, group, amount, currency, note):
        self._tid = tid
        self._date = tdate
        self._title = title
        self._group = group
        self._amount = amount
        self._currency = currency
        self._note = note

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

    @staticmethod
    def parse(row):
        parsers = [
            int,
            date,
            str,
            Group,
            float,
            str,
            str
        ]

        parsed = [func(val) for func, val in zip(parsers, row)]
        return Transaction(*parsed)


