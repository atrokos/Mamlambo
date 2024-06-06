import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from typing import Callable

from mamlambo.Transactions import Transaction
from mamlambo.Transactions.group import Group


class FiltersWindow(tk.Toplevel):
    """A window where the user can apply and define their own filters."""
    
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(1, weight=1)
        self._filter_data = dict()
        self._last_row = 0
        self._id_counter = 0  # Counter for the Filters' IDs.
        self._result = None
        self._setup_buttons()
        
    def get_results(self) -> list[Callable[[Transaction], bool]]:
        """Returns the list of created filters."""
        return self._result

    def _setup_buttons(self):
        ttk.Button(self, text="Add filter", command=self._new_filter
                   ).grid(row=0, column=0, sticky="nsw", padx=5, pady=5)
        ttk.Button(self, text="Confirm", command=self._confirm
                   ).grid(row=0, column=2, sticky="nse", padx=5, pady=5)
        self._new_filter()

    def _next_row(self):
        self._last_row += 1
        return self._last_row

    def _next_id(self):
        self._id_counter += 1
        return self._id_counter

    def _delete_filter(self, filter_id):
        """Remove the selected filter. If there is only one left, do not delete it."""
        if len(self._filter_data) <= 1:
            return

        data = self._filter_data[filter_id]
        data["Combobox"].destroy()
        data["Entry"].destroy()
        data["Button"].destroy()

        self._filter_data.pop(filter_id)

    def _new_filter(self):
        """Add a new filter to the bottom, giving it its ID and variables."""
        row = self._next_row()
        filter_id = self._next_id()

        combo = ttk.Combobox(self, values=Transaction.value_names, state="readonly")
        combo.grid(column=0, row=row, padx=5, pady=5)

        entry = ttk.Entry(self)
        entry.grid(column=1, row=row, sticky="nswe", pady=5)

        del_btn = ttk.Button(self, text="Remove", command=lambda: self._delete_filter(filter_id))
        del_btn.grid(column=2, row=row, padx=5, pady=5)

        self._filter_data[filter_id] = {
            "Combobox": combo,
            "Entry": entry,
            "Button": del_btn
        }

    def _confirm(self):
        """User clicked on confirm -> check that all filters are in a valid state and close the window."""
        try:
            self._result = self._retrieve_filters()
            self.destroy()
        except ValueError as e:
            mb.showerror("Wrong filter", str(e))
            self._result = None

    def _retrieve_filters(self):
        """
        Only retrieve filters with a selected property (nonempty Combobox) and check that their
        Entry box has valid values.
        """
        
        # Get filters with set property
        valid_filters = [fil for fil in self._filter_data.values() if fil["Combobox"].get() != ""]
        result = []

        for fil in valid_filters:
            result.append(self._parse_filter(fil))

        return result

    def _parse_filter(self, fil: dict) -> Callable[[Transaction], bool]:
        # This part uses a lot of functional programming, as it makes these kinds of
        # comparisons easier.

        # Split the entered data by " ", first should be the comparator, second
        # the compared value
        entry_split = fil["Entry"].get().split(" ", 1)
        if len(entry_split) == 2:
            comp = entry_split[0]
            value = entry_split[1]
        else:
            raise ValueError("The entry field should only contain two items: comparator and value.")

        # Depending on the property, validate the expected value and create a getter for said property
        match fil["Combobox"].get():
            case "Date":
                getter = lambda x: x.date
                parsed_value = Transaction.validate_date(value)
            case "Title":
                getter = lambda x: x.title
                parsed_value = value
            case "Group":
                getter = lambda x: x.group
                parsed_value = Group(value)
            case "Amount":
                getter = lambda x: x.amount
                parsed_value = Transaction.validate_amount(value)
            case "Currency":
                getter = lambda x: x.currency
                parsed_value = Transaction.validate_currency(value)
            case "Description":
                getter = lambda x: x.note
                parsed_value = value
            case _:
                raise ValueError("Unknown property!")

        # Depending on the comparator, return the complete filtering function
        match comp:
            case ">":
                return lambda x: getter(x) > parsed_value
            case "<":
                return lambda x: getter(x) < parsed_value
            case "==":
                return lambda x: getter(x) == parsed_value
            case ">=":
                return lambda x: getter(x) >= parsed_value
            case "<=":
                return lambda x: getter(x) <= parsed_value
            case "!=":
                return lambda x: getter(x) != parsed_value
            case _:
                raise ValueError(f"Unknown comparator: {comp}")
