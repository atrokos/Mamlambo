from datetime import date
from src.Transactions.group import Group


class Transaction:
    value_names = [
        "Date", "Title", "Group", "Amount", "Description"
    ]

    def __init__(self, tdate: date, title: str, group, amount, currency, note):
        self._date = tdate
        self._title = title
        self._group = group
        self._amount = amount
        self._currency = currency
        self._note = note

    def __eq__(self, other):
        if isinstance(other, Transaction):
            return (self._date == other._date and
                    self._title == other._title and
                    self._group == other._group and
                    self._amount == other._amount and
                    self._currency == other._currency and
                    self._note == other._note)
        return False

    def to_dict(self) -> dict[str, str]:
        result = dict()
        values = self.dump()
        result["Date"] = values[0]
        result["Title"] = values[1]
        result["Group"] = values[2]
        result["Amount"] = values[3] + " " + values[4]
        result["Description"] = values[5]
        return result

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
            date.fromisoformat,
            str,
            Group,
            float,
            str,
            str
        ]

        parsed = [func(val) for func, val in zip(parsers, row)]
        return Transaction(*parsed)

    def dump(self):
        values = [
            self._date,
            self._title,
            self._group,
            self._amount,
            self._currency,
            self._note
        ]
        return [str(val) for val in values]


