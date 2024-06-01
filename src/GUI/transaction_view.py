import tkinter as tk
from tkinter import ttk

from src.Database.database_wrapper import DatabaseView
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

    def populate_tree(self, transactions: list[Transaction]):
        counter = 0
        # Clear existing items
        self.delete(*self.get_children())

        # Add data to the tree view
        for transaction in transactions:
            if transaction is None:
                continue

            self.insert("", "end", id=counter, values=(
                transaction.date,
                transaction.title,
                transaction.group,
                transaction.amount,
                transaction.currency,
                transaction.description
            ))

            counter += 1


class TransactionPages(tk.Frame):
    """
    Contains all logic for rendering the Transactions table, along with
    page switching and accessing the database for rendered data.
    """
    def __init__(self, master, database):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.database: DatabaseView = database
        self.treeview = None
        self.next_btn = None
        self.prev_btn = None
        self.curr_page = 0
        self.items_per_page = 10
        self._setup_treeview()
        self._setup_buttons()

    def set_database(self, database):
        self.database = database
        self.database.subscribe(self.refresh)

    def set_items_per_page(self, items: int):
        if items <= 0:
            return

        self.items_per_page = items
        self.refresh()

    def refresh(self):
        if self.database is None:
            return

        self.treeview.populate_tree(self._get_page(self.curr_page))

    def _setup_treeview(self):
        self.treeview = TransactionTreeView(self)
        self.treeview.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def _setup_buttons(self):
        self.prev_btn = ttk.Button(self, text="Previous", command=self._prev_page)
        self.prev_btn.grid(row=1, column=0, padx=5, pady=5, sticky="nsw")
        self.next_btn = ttk.Button(self, text="Next", command=self._next_page)
        self.next_btn.grid(row=1, column=1, padx=5, pady=5, sticky="nse")

        # Set both buttons to `disabled`
        self.prev_btn["state"] = "disabled"
        self.next_btn["state"] = "disabled"

    def _next_page(self):
        self.curr_page += 1
        self.treeview.populate_tree(self._get_page(self.curr_page))
    
    def _get_page(self, page_number):
        """Returns only a given slice of data."""
        start = page_number * self.items_per_page
        end = start + self.items_per_page

        if start == 0:
            self.prev_btn["state"] = "disabled"
        else:
            self.prev_btn["state"] = "normal"

        if end >= len(self.database):
            self.next_btn["state"] = "disabled"
            end = len(self.database)
        else:
            self.next_btn["state"] = "normal"

        return self.database[start:end]

    def _prev_page(self):
        if self.curr_page > 0:
            self.curr_page -= 1

        self.treeview.populate_tree(self._get_page(self.curr_page))

    def get_selection(self):
        offset = self.curr_page * self.items_per_page
        return [offset + int(x) for x in self.treeview.selection()]


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


