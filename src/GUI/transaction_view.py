import tkinter as tk
from tkinter import ttk

from src.Transactions import Transaction


class TransactionTreeView(ttk.Treeview):
    def __init__(self, parent):
        super().__init__(parent, show="headings")
        self["columns"] = ("Date", "Title", "Tags", "Amount", "Currency", "Description")

        self.heading("#1", text="Date")
        self.column("#1", width=80)
        self.heading("#2", text="Title")
        self.heading("#3", text="Tags")
        self.heading("#4", text="Amount")
        self.heading("#5", text="Currency")
        self.column("#5", width=60)
        self.heading("#6", text="Description")

    def populate_tree(self, transactions):
        # Clear existing items
        self.delete(*self.get_children())

        # Add data to the tree view
        for transaction in transactions:
            if transaction is None:
                continue

            self.insert("", "end", values=(
                transaction.date,
                transaction.title,
                transaction.group,
                transaction.amount,
                transaction.currency,
                transaction.description
            ))


if __name__ == "__main__":
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
    root = tk.Tk()
    root.title("Transaction Table")

    tree = TransactionTreeView(root)
    tree.populate_tree(transactions)
    tree.grid(row=0, column=0, sticky="nsew")

    root.mainloop()


