import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

from mamlambo.Transactions import Transaction


class TransactionWindow(tk.Toplevel):
    """
    A window for adding or editing a transaction.

    :param master: The parent window.
    :param templates: Optional dictionary of templates.
    :param transaction: Optional Transaction object to edit.
    """
    def __init__(self, master, templates=None, transaction: Transaction | None = None):
        super().__init__(master)

        self.title('Add Transaction')
        self.resizable(True, False)
        self.columnconfigure(1, weight=1)
        self._values = dict()
        self.result = None
        self.templates = templates
        self.template_sel = None

        self._setup_all()

        if transaction is not None:
            self.title("Edit Transaction")
            self._set_transaction(transaction)

    def get_transaction(self):
        """
        Get the transaction created or edited in the window.

        :return: The Transaction object or None.
        """
        return self.result

    def _setup_all(self):
        """Set up all widgets in the window."""
        self._setup_template_sel()
        self._setup_entries()
        self._setup_buttons()
        self.protocol("WM_DELETE_WINDOW", self._cancel_event)

    def _delete_template(self):
        """
        Delete the selected template after user confirmation.
        """
        confirmation = mb.askyesno(title="Delete Template", message="Are you sure you want to delete this template?")
        if confirmation:
            template_name = self.template_sel.get()
            options = list(self.template_sel['values'])
            options.remove(template_name)
            self.template_sel['values'] = options
            self.template_sel.set("")
            self.templates.pop(template_name)

    def _set_transaction(self, transaction: Transaction):
        """
        Set the transaction to be edited in the window.

        :param transaction: The Transaction object to edit.
        """
        self._values["Date"].set(transaction.date)
        self._values["Title"].set(transaction.title)
        self._values["Group"].set(transaction.group)
        self._values["Amount"].set(f"{transaction.amount} {transaction.currency}")
        self._values["Description"].set(transaction.description)

    def _confirm_event(self):
        """
        Confirm the creation or editing of the transaction and close the window.
        """
        data = self._create_transaction_data()
        try:
            self.result = Transaction.parse(data)
        except ValueError as e:
            mb.showerror("Incorrect format", str(e))
            return

        self.destroy()

    def _create_transaction_data(self):
        """
        Create a list of transaction data from the user input.

        :return: A list of transaction data.
        """
        amount = self._values["Amount"].get().split(" ")
        if len(amount) != 2:
            mb.showerror("Incorrect format", "Currency has to follow this format: \"<amount> <ISO code>\"")
            return
        data = [
            self._values["Date"].get(),
            self._values["Title"].get(),
            self._values["Group"].get(),
            amount[0],
            amount[1],
            self._values["Description"].get()
        ]
        return data

    def _save_template_event(self):
        """
        Save the current transaction as a template.
        """
        name_getter = EntryWindow(self, title="Create Template", label="Template name")
        name_getter.grab_set()
        name_getter.wait_window()
        template_name = name_getter.get_result()

        template = self._add_template(template_name)

        self.templates[template_name] = template

    def _add_template(self, template_name: str):
        """
        Add a new template to the templates dictionary.

        :param template_name: The name of the new template.
        :return: The created template dictionary.
        """
        template = {key: value.get() for key, value in self._values.items()}
        if template_name not in self.template_sel['values']:
            options = list(self.template_sel['values'])
            options.append(template_name)
            self.template_sel['values'] = sorted(options)
            self.template_sel.set(template_name)

        return template

    def _cancel_event(self):
        """
        Cancel the transaction creation or editing and close the window.
        """
        self._values = None
        self.destroy()

    def _update_template(self, event=None):
        """
        Update the input fields with the selected template data.
        """
        template_name = self.template_sel.get()

        if template_name == "":
            return

        for entry, value in self.templates[template_name].items():
            if entry == "Currency":
                self._values["Amount"].set(self._values["Amount"].get() + " " + value)  # Append currency to the amount
                continue
            self._values[entry].set(value)

    def _next_row(self):
        """
        Get the next available row in the grid.

        :return: The next available row index.
        """
        return self.grid_size()[1]

    def _setup_buttons(self):
        """Set up the buttons in the window."""
        button_row = self._next_row()
        ttk.Button(self, text="Cancel", command=self._cancel_event
                   ).grid(row=button_row, column=0, sticky="w", pady=(10, 5), padx=5)
        ttk.Button(self, text="Save as Template", command=self._save_template_event
                   ).grid(row=button_row, column=1, sticky="w", pady=(10, 5), padx=5)
        ttk.Button(self, text="Confirm", command=self._confirm_event
                   ).grid(row=button_row, column=2, sticky="e", pady=(10, 5), padx=5)

    def _setup_template_sel(self):
        """Set up the template selection widgets."""
        template_names = sorted(self.templates.keys())
        box_row = self._next_row()
        ttk.Label(self, text="Template").grid(row=box_row, column=0, sticky="w", pady=(0, 8))
        self.template_sel = ttk.Combobox(self, values=template_names, state='readonly')
        self.template_sel.bind("<<ComboboxSelected>>", self._update_template)
        self.template_sel.grid(row=box_row, column=1, sticky='ew', pady=(0, 8))
        ttk.Button(self, text="Delete", command=self._delete_template
                   ).grid(row=box_row, column=2, sticky='w', pady=(0, 8))

    def _setup_entries(self):
        """Set up the entry widgets for transaction details."""
        for entry in Transaction.value_names:
            if entry == "Currency":  # Currency is included in the "Amount" entry
                continue
            self._values[entry] = tk.StringVar()
            row = self._next_row()
            ttk.Label(self, text=entry).grid(row=row, column=0, sticky="w", pady=(0, 8), padx=(5, 0))
            ttk.Entry(self, textvariable=self._values[entry]
                      ).grid(row=row, column=1, columnspan=2, sticky="ew", pady=(0, 8), padx=(0, 10))


class EntryWindow(tk.Toplevel):
    """
    A simple window to get a single string input from the user.

    :param master: The parent window.
    :param title: The title of the window.
    :param label: The label text for the entry field.
    """
    def __init__(self, master, /, title, label):
        super().__init__(master)
        self.result = tk.StringVar()
        self.title(title)
        ttk.Label(self, text=label).grid(row=0, column=0, sticky="w", pady=(5, 8), padx=5)
        ttk.Entry(self, textvariable=self.result).grid(row=0, column=1, sticky="ew", pady=(5, 8), padx=5)
        ttk.Button(self, text="Cancel", command=self.cancel).grid(row=1, column=0, sticky="w", pady=(0, 8), padx=5)
        ttk.Button(self, text="Confirm", command=self.confirm).grid(row=1, column=1, sticky="e", pady=(0, 8), padx=5)

    def cancel(self):
        """Cancel the input and close the window."""
        self.result = tk.StringVar()  # Reset the variable if user cancels the action
        self.destroy()

    def confirm(self):
        """Confirm the input and close the window."""
        self.destroy()

    def get_result(self):
        """
        Get the result of the user input.

        :return: The input string.
        """
        return self.result.get()
