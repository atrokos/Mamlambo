import tkinter as tk
from tkinter import ttk
from typing import Callable

from mamlambo.Database.database_view import DatabaseView
from mamlambo.Transactions import Transaction
from mamlambo.Enums.enums import Order, Property
from collections import namedtuple


# A named tuple that holds the information about the current sorting.
OrderState = namedtuple("OrderState", ["property", "order"])


class TransactionPagesFrame(tk.Frame):
    """
    Contains all logic for rendering the Transactions table, along with
    page switching and accessing the database for rendered data.
    """

    def __init__(self, master, database):
        """Initialize the frame with treeview and navigation buttons."""
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.database: DatabaseView = database
        self.treeview = None
        self.next_btn = None
        self.prev_btn = None
        self.curr_page = 0
        self.items_per_page = 10
        self.order_state: OrderState = OrderState(Property.DATE, Order.DESC)
        self._setup_treeview()
        self._setup_buttons()

    def set_database(self, database):
        """Set the database and subscribe to its changes."""
        self.database = database
        self.database.subscribe(self.refresh)

    def set_items_per_page(self, items: int):
        """Set the number of items to display per page."""
        if items <= 0:
            return

        self.items_per_page = items
        self.refresh()

    def refresh(self):
        """Refresh the treeview with the current page of transactions."""
        if self.database is None:
            return

        self.treeview.populate_tree(self._get_page(self.curr_page))

    def get_selection(self):
        """Get the selected transactions from the treeview."""
        offset = self.curr_page * self.items_per_page
        return [offset + int(x) for x in self.treeview.selection()]

    def sort_by(self, prop: Property):
        """Sort the transactions by the given property."""
        if prop == self.order_state.property:
            # If the properties are the same, simply switch the order
            new_order = (self.order_state.order.value + 1) % 2
            self.order_state = self.order_state._replace(order=Order(new_order))
        else:
            # Otherwise change the order to `descending`
            self.order_state = OrderState(property=prop, order=Order.DESC)

        self._order_columns()

    def _setup_treeview(self):
        """Set up the treeview for displaying transactions."""
        self.treeview = TransactionTreeView(self)
        self.treeview.bind_column_press(self.sort_by)
        self.treeview.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def _setup_buttons(self):
        """Set up the navigation buttons for paging through transactions."""
        self.prev_btn = ttk.Button(self, text="Previous", command=self._prev_page)
        self.prev_btn.grid(row=1, column=0, padx=5, pady=5, sticky="nsw")
        self.next_btn = ttk.Button(self, text="Next", command=self._next_page)
        self.next_btn.grid(row=1, column=1, padx=5, pady=5, sticky="nse")

        # Set both buttons to `disabled`
        self.prev_btn["state"] = "disabled"
        self.next_btn["state"] = "disabled"

    def _next_page(self):
        """Move to the next page of transactions."""
        self.curr_page += 1
        self.treeview.populate_tree(self._get_page(self.curr_page))

    def _get_page(self, page_number):
        """Returns only a given slice of data. Enables/disables page switching buttons depending on page number."""
        start = page_number * self.items_per_page
        if start > len(self.database):
            self.curr_page = 0
            start = 0

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
        """Move to the previous page of transactions."""
        if self.curr_page > 0:
            self.curr_page -= 1

        self.treeview.populate_tree(self._get_page(self.curr_page))

    def _order_columns(self):
        """Order the transactions according to the current order state."""
        if self.database is None:
            return

        # Orders data according to `self.order_state`
        reverse = True if self.order_state.order == Order.DESC else False

        match self.order_state.property:
            case Property.DATE:
                key = lambda x: x.date
            case Property.TITLE:
                key = lambda x: x.title
            case Property.GROUP:
                key = lambda x: x.group
            case Property.AMOUNT:
                key = lambda x: x.amount
            case Property.CURRENCY:
                key = lambda x: x.currency
            case _:
                return

        self.database.sort_by(sort_key=key, reverse=reverse)
        # Go to the beginning when changing entry order
        self.curr_page = 0
        self.treeview.populate_tree(self._get_page(self.curr_page))


class TransactionTreeView(ttk.Treeview):
    def __init__(self, parent):
        """Initialize the treeview for displaying transaction details."""
        super().__init__(parent, show="headings")
        self["columns"] = ("Date", "Title", "Group", "Amount", "Currency", "Description")

        self.heading("#1", text="Date")
        self.column("#1", width=80)
        self.heading("#2", text="Title")
        self.heading("#3", text="Group")
        self.heading("#4", text="Amount")
        self.heading("#5", text="Currency")
        self.column("#5", width=60)
        self.heading("#6", text="Description")

    def populate_tree(self, transactions: list[Transaction]):
        """Populate the treeview with a list of transactions."""
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

    def bind_column_press(self, function: Callable[[Property], None]):
        """
        Binds the columns to the given function, giving the selected property as an argument.
        The Description property is never bound.
        """
        self.heading(f"#1", command=lambda: function(Property.DATE))
        self.heading(f"#2", command=lambda: function(Property.TITLE))
        self.heading(f"#3", command=lambda: function(Property.GROUP))
        self.heading(f"#4", command=lambda: function(Property.AMOUNT))
        self.heading(f"#5", command=lambda: function(Property.CURRENCY))
