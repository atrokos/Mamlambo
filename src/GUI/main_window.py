import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd
import tkinter.messagebox as mb


from src.Database.database_wrapper import DatabaseView
from src.GUI.about_window import AboutWindow
from src.GUI.add_transaction import TransactionWindow
from src.GUI.button_row import ButtonRow
from src.GUI.filters_window import FiltersWindow
from src.GUI.transactions_list import TransactionPages


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Mamlambo")  # Set the window title
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self._left_ribbon = None
        self._right_ribbon = None
        self.trns_pages: TransactionPages | None = None
        self.database: DatabaseView | None = None
        self.templates = {
            "Test": {
                "Date": "2024-05-31",
                "Title": "Test",
                "Group": "Test",
                "Amount": "-256",
                "Currency": "CZK",
                "Description": "Test"
            }
        }

        self.setup_menu()
        self.setup_ribbon()
        self.setup_transaction_view()
        self.update_buttons()

    def setup_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='New', command=self.new_session)
        file_menu.add_command(label="Open", command=self.open_session)
        file_menu.add_command(label="Save", command=self.save_session)
        file_menu.add_command(label='Exit without saving', command=self.destroy)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Convert currency")
        tools_menu.add_command(label="Statistics")

        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="CSV")
        options_menu.add_command(label="Commits")

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.display_about)

        menubar.add_cascade(label='File', menu=file_menu)
        menubar.add_cascade(label='Tools', menu=tools_menu)
        menubar.add_cascade(label='Options', menu=options_menu)
        menubar.add_cascade(label='Help', menu=help_menu)
        self.config(menu=menubar)  # Set the menubar for the main window

    def new_session(self):
        answer = self._check_saved_commited()
        if not answer:
            return

        self.database = DatabaseView(lambda x: x.date, True)
        self.database.subscribe(self.update_buttons)
        self.trns_pages.set_database(self.database)
        self._left_ribbon.enable_all()

    def _check_saved_commited(self) -> bool:
        if self.database is not None:
            if not self.database.all_commited():
                answer = mb.askyesno("Confirmation", "Not all changes were commited, all uncommited data will be "
                                                     "lost.\nContinue?")
                return answer
            if not self.database.is_saved():
                answer = mb.askyesno("Confirmation", "This session was not saved, all unsaved data will be lost.\n" +
                                     "Continue?")
                return answer
        return True

    def open_session(self):
        answer = self._check_saved_commited()
        if not answer:
            return

        filename = fd.askopenfilename()
        if filename == "":
            return
        self.database = DatabaseView(lambda x: x.date, True)
        self.database.subscribe(self.update_buttons)
        self.trns_pages.set_database(self.database)
        self.database.load(filename, defaultorder=lambda x: x.date)
        self._left_ribbon.enable_all()

    def save_session(self):
        if self.database is None:
            mb.showinfo("Empty database", "No database was created.")
            return

        if not self.database.all_commited():
            answer = mb.askyesno("Confirmation", "Not all changes were commited, do you want to continue?")
            if not answer:
                return

        filename = fd.asksaveasfilename(confirmoverwrite=True,
                                        defaultextension=".*",
                                        filetypes=[("Comma Separated Values", "*.csv"),
                                                   ("JavaScript Object Notation", "*.json")])
        if filename == "":
            return
        try:
            self.database.dump(Path(filename))
        except ValueError as e:
            mb.showerror("Unsupported file type", str(e))

    def display_about(self):
        AboutWindow(self, "0.1.5 alpha")

    def setup_ribbon(self):
        self._left_ribbon = ButtonRow(self)
        self._left_ribbon.grid(row=0, column=0, sticky='nsw')

        self._left_ribbon.add_button("Add", command=self.add_trn_comm)
        self._left_ribbon.add_button("Edit", command=self.edit_trn_comm)
        self._left_ribbon.add_button("Remove", command=self.remove_trn_comm)
        self._left_ribbon.add_button("Filter", command=self.filter_comm)
        self._left_ribbon.disable_all()

        self._right_ribbon = ButtonRow(self)
        self._right_ribbon.grid(row=0, column=1, sticky="nse")

        self._right_ribbon.add_button("Revert", command=self.revert_comm)
        self._right_ribbon.add_button("Commit", command=self.commit_comm)

    def nothing(self, event=None):
        pass

    def filter_comm(self):
        filter_window = FiltersWindow(self)
        filter_window.grab_set()
        filter_window.wait_window()

        filters = filter_window.get_results()
        self.database.sort_by(lambda x: x.date, filters=filters)

    def add_trn_comm(self):
        transaction_window = TransactionWindow(self, templates=self.templates)
        transaction_window.grab_set()
        transaction_window.wait_window()

        if transaction_window.values is None:
            return

        self.database.add(transaction_window.get_transaction())

    def edit_trn_comm(self):
        selected = self.trns_pages.get_selection()
        for index in selected:
            trn_dict = self.database[index].to_dict()
            edit_window = TransactionWindow(self, self.templates, trn_dict)
            edit_window.grab_set()
            edit_window.wait_window()

            if edit_window.values is None:
                return
            self.database.edit(index, edit_window.get_transaction())

    def remove_trn_comm(self):
        selected = self.trns_pages.get_selection()
        for index in selected:
            self.database.remove(index)

    def commit_comm(self):
        self.database.commit()

    def revert_comm(self):
        self.database.revert()

    def setup_transaction_view(self):
        self.trns_pages = TransactionPages(self, None)
        self.trns_pages.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky='nsew')

    def update_buttons(self):
        if self.database is None:
            self._right_ribbon.disable_all()
            return

        if self.database.can_revert():
            self._right_ribbon["revert"]["state"] = "normal"
        else:
            self._right_ribbon["revert"]["state"] = "disable"

        if not self.database.all_commited():
            self._right_ribbon["commit"]["state"] = "normal"
        else:
            self._right_ribbon["commit"]["state"] = "disable"


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
