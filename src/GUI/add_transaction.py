import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

from src.Transactions import Transaction


# TODO Check that values are valid
# TODO Correctly parse value and date

class TransactionWindow(tk.Toplevel):
    def __init__(self, master, templates=None, defaults: dict | None = None):
        super().__init__(master)

        self.title('Add Transaction')
        self.resizable(True, False)
        self.columnconfigure(1, weight=1)
        self.values = dict()
        self.templates = templates
        self.template_sel = None

        self.setup()

        if defaults is not None:
            self.title("Edit Transaction")
            for entry, value in defaults.items():
                self.values[entry].set(value)

    def setup(self):
        self._setup_template_sel()
        self._setup_entries()
        self._setup_buttons()
        self.protocol("WM_DELETE_WINDOW", self.cancel_event)

    def delete_template(self):
        confirmation = mb.askyesno(title="Delete Template", message="Are you sure you want to delete this template?")
        if confirmation:
            template_name = self.template_sel.get()
            options = list(self.template_sel['values'])
            options.remove(template_name)
            self.template_sel['values'] = options
            self.template_sel.set("")
            self.templates.pop(template_name)

    def confirm_event(self):
        self.destroy()

    def save_template_event(self):
        name_getter = EntryWindow(self, title="Create Template", label="Template name")
        name_getter.grab_set()
        name_getter.wait_window()
        template_name = name_getter.get_result()

        template = {key: value.get() for key, value in self.values.items()}
        if template_name not in self.template_sel['values']:
            options = list(self.template_sel['values'])
            options.append(template_name)
            self.template_sel['values'] = sorted(options)
            self.template_sel.set(template_name)
        self.templates[template_name] = template

    def cancel_event(self):
        self.values = None
        self.destroy()

    def update_template(self, event=None):
        template_name = self.template_sel.get()

        if template_name == "":
            return

        for entry, value in self.templates[template_name].items():
            self.values[entry].set(value)

    def _setup_buttons(self):
        button_row = self.next_row()
        ttk.Button(self, text="Cancel", command=self.cancel_event
                   ).grid(row=button_row, column=0, sticky="w", pady=(10, 5), padx=5)
        ttk.Button(self, text="Save as Template", command=self.save_template_event
                   ).grid(row=button_row, column=1, sticky="w", pady=(10, 5), padx=5)
        ttk.Button(self, text="Confirm", command=self.confirm_event
                   ).grid(row=button_row, column=2, sticky="e", pady=(10, 5), padx=5)

    def get_transaction(self):
        if self.values is None:
            return None

        # TODO nicer way
        amount = self.values["Amount"].get().split(" ")
        data = [
            self.values["Date"].get(),
            self.values["Title"].get(),
            self.values["Group"].get(),
            amount[0],
            amount[1],
            self.values["Description"].get()
        ]
        return Transaction.parse(data)

    def next_row(self):
        return self.grid_size()[1]

    def _setup_template_sel(self):
        template_names = sorted(self.templates.keys())
        box_row = self.next_row()
        ttk.Label(self, text="Template").grid(row=box_row, column=0, sticky="w", pady=(0, 8))
        self.template_sel = ttk.Combobox(self, values=template_names, state='readonly')
        self.template_sel.bind("<<ComboboxSelected>>", self.update_template)
        self.template_sel.grid(row=box_row, column=1, sticky='ew', pady=(0, 8))
        ttk.Button(self, text="Delete", command=self.delete_template
                   ).grid(row=box_row, column=2, sticky='w', pady=(0, 8))

    def _setup_entries(self):
        for entry in Transaction.value_names:
            self.values[entry] = tk.StringVar()
            row = self.next_row()
            ttk.Label(self, text=entry).grid(row=row, column=0, sticky="w", pady=(0, 8), padx=(5, 0))
            ttk.Entry(self, textvariable=self.values[entry]
                      ).grid(row=row, column=1, columnspan=2, sticky="ew", pady=(0, 8), padx=(0, 10))


class EntryWindow(tk.Toplevel):
    def __init__(self, master, /, title, label):
        super().__init__(master)
        self.result = tk.StringVar()
        self.title(title)
        ttk.Label(self, text=label).grid(row=0, column=0, sticky="w", pady=(5, 8), padx=5)
        ttk.Entry(self, textvariable=self.result).grid(row=0, column=1, sticky="ew", pady=(5, 8), padx=5)
        ttk.Button(self, text="Cancel", command=self.cancel).grid(row=1, column=0, sticky="w", pady=(0, 8), padx=5)
        ttk.Button(self, text="Confirm", command=self.confirm).grid(row=1, column=1, sticky="e", pady=(0, 8), padx=5)

    def cancel(self):
        self.result = tk.StringVar()  # Reset the variable if user cancels the action
        self.destroy()

    def confirm(self):
        self.destroy()

    def get_result(self):
        return self.result.get()


if __name__ == '__main__':
    root = tk.Tk()
    templates = {
        "Income": {
            "Date": "",
            "Title": "Work pay",
            "Group": "Incomes::Work",
            "Amount": "CZK",
            "Description": "Money from work"
        }, "Going out": {
            "Date": "",
            "Title": "Going drinking",
            "Group": "Expenses::goingOut",
            "Amount": "CZK",
            "Description": "Going out"
        }, "Subscriptions": {
            "Date": "2024-xx-01",
            "Title": "Subscriptions",
            "Group": "Expenses::Subscriptions",
            "Amount": "1500 CZK",
            "Description": "Subscriptions for all services"
        }
    }
    app = TransactionWindow(root, templates)
    app.grab_set()
    root.mainloop()


