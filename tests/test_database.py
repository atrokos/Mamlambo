from unittest import TestCase

from src.Database.database import Database
from src.Transactions import Transaction


class TestDatabase(TestCase):
    transactions = [
        Transaction.parse(["2024-05-29", "Test1", "incomes::gifts", "410", "CZK", ""]),
        Transaction.parse(["2024-05-29", "Test2", "incomes::work", "15000", "CZK", ""]),
        Transaction.parse(["2024-05-29", "Test3", "expenses", "-58", "CZK", ""]),
        Transaction.parse(["2024-05-29", "Test4", "incomes", "560.5", "CZK", ""]),
        Transaction.parse(["2024-05-30", "Test5", "expenses::amenities", "-2600.7", "CZK", ""]),
        Transaction.parse(["2024-05-30", "Test6", "expenses::drinks", "-650", "CZK", ""]),
        Transaction.parse(["2024-05-30", "Test7", "incomes::gifts", "780", "CZK", ""]),
        Transaction.parse(["2024-05-30", "Test8", "expenses::snacks", "-33", "CZK", ""]),
        Transaction.parse(["2024-05-30", "Test9", "incomes::gifts", "63.5", "CZK", ""]),
        Transaction.parse(["2024-05-30", "Test10", "expenses::drinks", "-25.6", "CZK", ""])
    ]

    def setUp(self):
        self.database = Database()

    def test_load(self):
        pass

    def test_dump(self):
        pass

    def test_commit(self):
        for transaction in self.transactions:
            self.database.add(transaction)

        if len(self.database) != 0:
            self.fail("Database should be empty")

        self.database.commit()

        if len(self.database) == 0:
            self.fail("Database should NOT be empty")

    def test_revert(self):
        for transaction in self.transactions:
            self.database.add(transaction)

        to_update = {0, 5, 7, 9}
        new_trns = [
            Transaction.parse(["2024-05-30", "Test1u", "incomes::gifts", "780", "CZK", ""]),
            Transaction.parse(["2024-05-30", "Test6u", "expenses::snacks", "-33", "CZK", ""]),
            Transaction.parse(["2024-05-30", "Test8u", "incomes::gifts", "63.5", "CZK", ""]),
            Transaction.parse(["2024-05-30", "Test10u", "expenses::drinks", "-25.6", "CZK", ""])
        ]
        self.database.commit()
        for index, transaction in zip(to_update, new_trns):
            self.database.update(index, transaction)

        self.database.commit()

        self.database.revert()

        for actual, expected in zip(self.database, self.transactions):
            self.assertEqual(actual, expected)

    def test_select(self):
        pass

    def test_add(self):
        for transaction in self.transactions:
            self.database.add(transaction)

        self.database.commit()

        if len(self.database) != len(self.transactions):
            self.fail("Not all transactions were added")

        for expected, actual in zip(self.transactions, self.database):
            self.assertEqual(expected, actual,
                             msg="The following transactions are not equal:\n{}\n{}".format(expected, actual))

    def test_update(self):
        for transaction in self.transactions:
            self.database.add(transaction)

        to_update = {0, 5, 7, 9}
        new_trns = [
            Transaction.parse(["2024-05-30", "Test1u", "incomes::gifts", "780", "CZK", ""]),
            Transaction.parse(["2024-05-30", "Test6u", "expenses::snacks", "-33", "CZK", ""]),
            Transaction.parse(["2024-05-30", "Test8u", "incomes::gifts", "63.5", "CZK", ""]),
            Transaction.parse(["2024-05-30", "Test10u", "expenses::drinks", "-25.6", "CZK", ""])
        ]
        self.database.commit()
        for index, transaction in zip(to_update, new_trns):
            self.database.update(index, transaction)

        self.database.commit()
        for index, transaction in enumerate(self.database):
            if index in to_update:
                if not transaction.title.endswith("u"):
                    self.fail("Transaction title should end with u (ie should be updated)")

        if len(self.database) != len(self.transactions):
            self.fail("There are to be more transactions than expected")

    def test_remove(self):
        for transaction in self.transactions:
            self.database.add(transaction)

        to_remove = [0, 5, 6, 9]

        self.database.commit()
        for index in to_remove:
            self.database.remove(index)

        self.database.commit()
        for index, transaction in enumerate(self.database):
            if transaction is None:
                to_remove.remove(index)

        if len(to_remove) != 0:
            self.fail("Not all required transactions were removed")
