import tkinter as tk
from tkinter import ttk
from typing import Any

from mamlambo.Transactions.converter import Converter


class ConversionWindow(tk.Toplevel):
    """A window where the user can convert between defined currencies."""
    
    def __init__(self, master, conversions: list[dict[str, Any]]):
        super().__init__(master)
        self.title("Currency conversion")
        self.resizable(False, False)

        self._converter = Converter(conversions)
        self._from_box = None
        self._to_box = None
        self._result_var = tk.StringVar()
        self._amount_var = tk.StringVar()
        self._setup_all()

    def _setup_all(self) -> None:
        self._setup_labels()
        self._setup_comboboxes()
        self._setup_entries_button()

    def _update_to_box(self, event=None) -> None:
        """When a `From` currency was selected, update the available `To` currencies."""
        avail_values = self._converter.get_available_conversions(self._from_box.get())
        self._to_box["values"] = avail_values

    def _convert(self) -> None:
        """Show the converted value after clicking on the `Convert` button."""
        amount = self._amount_var.get()
        try:
            amount_float = float(amount)
        except ValueError:
            self._result_var.set("Invalid amount.")
            return

        from_currency = self._from_box.get()
        to_currency = self._to_box.get()
        self._result_var.set(self._converter.convert(from_currency, to_currency, amount_float))

    def _setup_labels(self) -> None:
        ttk.Label(self, text="Currency converter", font="bold"
                  ).grid(row=0, column=0, columnspan=2, sticky="nsw", padx=5, pady=5)
        ttk.Label(self, text="From:").grid(row=1, column=0, sticky="nsw", padx=5, pady=5)
        ttk.Label(self, text="To:").grid(row=1, column=2, sticky="nsw", padx=5, pady=5)
        ttk.Label(self, text="Amount:").grid(row=2, column=0, sticky="nsw", padx=5, pady=5)
        ttk.Label(self, text="Result:").grid(row=3, column=0, sticky="nsw", padx=5, pady=5)

    def _setup_comboboxes(self) -> None:
        self._from_box = ttk.Combobox(self, values=self._converter.get_all_currencies())
        self._from_box.grid(row=1, column=1, sticky="nsw", padx=5, pady=5)
        self._from_box.bind("<<ComboboxSelected>>", self._update_to_box)
        self._to_box = ttk.Combobox(self, values=self._converter.get_all_currencies())
        self._to_box.grid(row=1, column=3, sticky="nsw", padx=5, pady=5)

    def _setup_entries_button(self) -> None:
        ttk.Entry(self, textvariable=self._amount_var).grid(row=2, column=1, sticky="nsw", padx=5, pady=5)
        tk.Entry(self, textvariable=self._result_var, fg="black", bg="white", bd=0, state="readonly"
                 ).grid(row=3, column=1, columnspan=5, sticky="nswe", padx=5, pady=5)

        ttk.Button(self, text="Convert", command=self._convert
                   ).grid(row=4, column=3, sticky="nse", padx=5, pady=5)

