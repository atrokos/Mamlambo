import tkinter as tk
from tkinter import filedialog as fd
import tkinter.messagebox as mb
from pathlib import Path

from mamlambo.Database import DatabaseView
from mamlambo.GUI.Windows import AboutWindow, TransactionWindow, FiltersWindow, StatisticsWindow
from mamlambo.GUI.Frames import TransactionPagesFrame, ButtonRowFrame
from mamlambo.Transactions import Transaction


class MainWindow(tk.Tk):
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()

        self.title("Mamlambo")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self._left_btn_row = None
        self._right_btn_row = None
        self.trns_pages: TransactionPagesFrame | None = None
        self._database: DatabaseView | None = None
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
        self.protocol("WM_DELETE_WINDOW", self.exit_app)

        self._setup_menu()
        self._setup_button_row()
        self._setup_transaction_view()
        self.update_buttons()

    def _setup_menu(self):
        """Set up the main menu of the application."""
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='New', command=self.new_session)
        file_menu.add_command(label="Open", command=self.open_session)
        file_menu.add_command(label="Save", command=self.save_session)
        file_menu.add_command(label='Exit', command=self.exit_app)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Convert currency")
        tools_menu.add_command(label="Statistics", command=self._show_stats)

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
        """Create a new database session."""
        answer = self._check_saved_committed()
        if not answer:
            return

        self._database = DatabaseView(lambda x: x.date, True)
        self._database.subscribe(self.update_buttons)
        self.trns_pages.set_database(self._database)
        self._left_btn_row.enable_all()

    def _check_saved_committed(self) -> bool:
        """
        Check if the database has uncommitted or unsaved changes.

        :return: True if it is safe to proceed, False otherwise.
        """
        if self._database is not None:
            if not self._database.all_committed():
                answer = mb.askyesno("Confirmation", "Not all changes were committed, all uncommitted data "
                                                     "will be lost.\nContinue?")
                return answer
            if not self._database.is_saved():
                answer = mb.askyesno("Confirmation", "This session was not saved, all unsaved data "
                                                     "will be lost.\nContinue?")
                return answer
        return True

    def open_session(self):
        """Open an existing database session from a file."""
        answer = self._check_saved_committed()
        if not answer:
            return

        filename = fd.askopenfilename(defaultextension=".csv")
        if filename == "":
            return
        self._database = DatabaseView(lambda x: x.date, True)
        self._database.subscribe(self.update_buttons)
        self.trns_pages.set_database(self._database)
        self._database.load(filename, Transaction.parse)
        self._left_btn_row.enable_all()

    def _show_stats(self):
        """Show statistics for the current database view. Sorts the data by date, ascending."""
        if self._database is None:
            return

        # Check that there is only a single currency in the currently shown data
        currency = None
        for i in range(len(self._database)):
            if currency is not None and currency != self._database[i].currency:
                mb.showinfo("More currencies", "Statistics work with only one type of currency."
                                               "Use a filter to have only one type of currency.")
                return
            currency = self._database[i].currency

        self._database.sort_by(sort_key=lambda x: x.date, reverse=False)

        stats_window = StatisticsWindow(self, self._database)
        stats_window.wait_window()

    def exit_app(self):
        """Handle the application exit event."""
        answer = self._check_saved_committed()
        if answer:
            self.destroy()

    def save_session(self):
        """Save the current database session to a file."""
        if self._database is None:
            mb.showinfo("Empty database", "No database was created.")
            return

        if not self._database.all_committed():
            answer = mb.askyesno("Confirmation", "Not all changes were committed, do you want to continue?")
            if not answer:
                return

        filename = fd.asksaveasfilename(confirmoverwrite=True,
                                        defaultextension=".*",
                                        filetypes=[("Comma Separated Values", "*.csv"),
                                                   ("JavaScript Object Notation", "*.json")])
        if filename == "":
            return
        try:
            self._database.dump(Path(filename))
        except ValueError as e:
            mb.showerror("Unsupported file type", str(e))

    def display_about(self):
        """Display the 'About' window."""
        AboutWindow(self, "0.9.0")

    def _setup_button_row(self):
        """Set up the row of buttons in the main window."""
        self._left_btn_row = ButtonRowFrame(self)
        self._left_btn_row.grid(row=0, column=0, sticky='nsw')

        self._left_btn_row.add_button("Add", command=self.add_trn_comm)
        self._left_btn_row.add_button("Edit", command=self.edit_trn_comm)
        self._left_btn_row.add_button("Remove", command=self.remove_trn_comm)
        self._left_btn_row.add_button("Filter", command=self.filter_comm)
        self._left_btn_row.disable_all()

        self._right_btn_row = ButtonRowFrame(self)
        self._right_btn_row.grid(row=0, column=1, sticky="nse")

        self._right_btn_row.add_button("Revert", command=self.revert_comm)
        self._right_btn_row.add_button("Commit", command=self.commit_comm)

    def filter_comm(self):
        """Open the filter window and apply selected filters to the database."""
        filter_window = FiltersWindow(self)
        filter_window.grab_set()
        filter_window.wait_window()

        filters = filter_window.get_results()
        self._database.sort_by(lambda x: x.date, filters=filters)

    def add_trn_comm(self):
        """Open the transaction window to add a new transaction."""
        transaction_window = TransactionWindow(self, templates=self.templates)
        transaction_window.grab_set()
        transaction_window.wait_window()

        if transaction_window.get_transaction() is None:
            return

        self._database.add(transaction_window.get_transaction())

    def edit_trn_comm(self):
        """Open the transaction window to edit selected transactions."""
        selected = self.trns_pages.get_selection()
        for index in selected:
            transaction = self._database[index]
            edit_window = TransactionWindow(self, templates=self.templates, transaction=transaction)
            edit_window.grab_set()
            edit_window.wait_window()

            if edit_window.get_transaction() is None:  # If the user cancelled the editing, don't change anything
                continue
            self._database.edit(index, edit_window.get_transaction())

    def remove_trn_comm(self):
        """Remove selected transactions from the database."""
        selected = self.trns_pages.get_selection()
        for index in selected:
            self._database.remove(index)

    def commit_comm(self):
        """Commit all changes to the database."""
        self._database.commit()

    def revert_comm(self):
        """Revert the last committed change."""
        self._database.revert()

    def _setup_transaction_view(self):
        """Set up the transaction pages view in the main window."""
        self.trns_pages = TransactionPagesFrame(self, None)
        self.trns_pages.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky='nsew')

    def update_buttons(self):
        """Update the state of the buttons based on the database state."""
        if self._database is None:
            self._right_btn_row.disable_all()
            return

        if self._database.can_revert():
            self._right_btn_row["revert"]["state"] = "normal"
        else:
            self._right_btn_row["revert"]["state"] = "disable"

        if not self._database.all_committed():
            self._right_btn_row["commit"]["state"] = "normal"
        else:
            self._right_btn_row["commit"]["state"] = "disable"
