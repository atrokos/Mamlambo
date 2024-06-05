import tkinter as tk
from tkinter import filedialog as fd
import tkinter.messagebox as mb
from pathlib import Path
import json

from mamlambo.Database import DatabaseView
from mamlambo.GUI.Windows import AboutWindow, TransactionWindow, FiltersWindow, StatisticsWindow
from mamlambo.GUI.Frames import TransactionPagesFrame, ButtonRowFrame
from mamlambo.GUI.Windows.conversion_window import ConversionWindow
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
        self._conversions = []
        self._templates = dict()
        self.protocol("WM_DELETE_WINDOW", self.exit_app)

        self._setup_menubar()
        self._setup_button_row()
        self._setup_transaction_view()
        self._update_buttons()
        self._load_config("./data/config.json")

    def _new_session(self):
        """Create a new database session."""
        answer = self._check_saved_committed()
        if not answer:
            return

        self._database = DatabaseView(lambda x: x.date, True)
        self._database.subscribe(self._update_buttons)
        self.trns_pages.set_database(self._database)
        self._left_btn_row.enable_all()

    def _open_session(self):
        """Open an existing database session from a file."""
        answer = self._check_saved_committed()
        if not answer:
            return

        filename = fd.askopenfilename(defaultextension=".csv")
        if filename == "":
            return
        self._database = DatabaseView(lambda x: x.date, True)
        self._database.subscribe(self._update_buttons)
        self.trns_pages.set_database(self._database)
        try:
            self._database.load(filename, Transaction.parse)
        except ValueError as e:
            mb.showerror("Import error", str(e))
            self._database = None
            return
        self._left_btn_row.enable_all()

    def _save_session(self):
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
            self._save_config("./data/config.json")
        except ValueError as e:
            mb.showerror("Unsupported file type", str(e))
        except IOError as e:
            mb.showerror("Database error", f"Could not save the database:\n{str(e)}")

    def exit_app(self):
        """Handle the application exit event."""
        answer = self._check_saved_committed()
        if answer:
            self.quit()
            self.destroy()

    def _show_conversion(self):
        ConversionWindow(self, self._conversions).focus_set()

    def _show_statistics(self):
        """Show statistics for the current database view. Sorts the data by date, ascending."""
        if self._database is None:
            mb.showinfo("No database", "There is no database connected.")
            return

        # Check that there is only a single currency in the currently shown data
        currency = None
        for i in range(len(self._database)):
            if currency is not None and currency != self._database[i].currency:
                mb.showinfo("More currencies", "Statistics work with only one type of currency."
                                               "Use a filter to have only one type of currency.")
                return
            currency = self._database[i].currency

        # Sort the database by date, ascending, so that the statistics window can plot the
        # "Balance" graph correctly
        self._database.sort_by(sort_key=lambda x: x.date, reverse=False)

        StatisticsWindow(self, self._database).focus_set()

    def _display_about(self):
        """Display the 'About' window."""
        AboutWindow(self, "0.9.0").focus_set()

    def _setup_menubar(self):
        """Set up the main menubar of the application."""
        menubar = tk.Menu(self)

        # "File" option
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='New', command=self._new_session)
        file_menu.add_command(label="Open", command=self._open_session)
        file_menu.add_command(label="Save", command=self._save_session)
        file_menu.add_command(label='Exit', command=self.exit_app)

        # "Tools" option
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Convert currency", command=self._show_conversion)
        tools_menu.add_command(label="Statistics", command=self._show_statistics)

        # "Help" option
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._display_about)

        menubar.add_cascade(label='File', menu=file_menu)
        menubar.add_cascade(label='Tools', menu=tools_menu)
        menubar.add_cascade(label='Help', menu=help_menu)
        self.config(menu=menubar)  # Set the menubar for the main window

    def _setup_button_row(self):
        """Set up the row of buttons in the main window."""
        self._left_btn_row = ButtonRowFrame(self)
        self._left_btn_row.grid(row=0, column=0, sticky='nsw')

        self._left_btn_row.add_button("Add", command=self._add_trn_comm)
        self._left_btn_row.add_button("Edit", command=self._edit_trn_comm)
        self._left_btn_row.add_button("Remove", command=self._remove_trn_comm)
        self._left_btn_row.add_button("Filter", command=self._filter_comm)
        self._left_btn_row.disable_all()

        self._right_btn_row = ButtonRowFrame(self)
        self._right_btn_row.grid(row=0, column=1, sticky="nse")

        self._right_btn_row.add_button("Revert", command=self._revert_comm)
        self._right_btn_row.add_button("Commit", command=self._commit_comm)

    def _setup_transaction_view(self):
        """Set up the transaction pages view in the main window."""
        self.trns_pages = TransactionPagesFrame(self, None)
        self.trns_pages.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky='nsew')

    def _add_trn_comm(self):
        """Open the transaction window to add a new transaction."""
        transaction_window = TransactionWindow(self, templates=self._templates)
        transaction_window.focus_set()
        transaction_window.grab_set()
        transaction_window.wait_window()

        if transaction_window.get_transaction() is None:  # If the user cancelled the adding, don't add anything
            return

        self._database.add(transaction_window.get_transaction())

    def _edit_trn_comm(self):
        """Open the transaction window to edit selected transactions."""
        selected = self.trns_pages.get_selection()
        for index in selected:
            transaction = self._database[index]
            edit_window = TransactionWindow(self, templates=self._templates, transaction=transaction)
            edit_window.focus_set()
            edit_window.grab_set()
            edit_window.wait_window()

            if edit_window.get_transaction() is None:  # If the user cancelled the editing, don't change anything
                continue
            self._database.edit(index, edit_window.get_transaction())

    def _remove_trn_comm(self):
        """Remove selected transactions from the database."""
        selected = self.trns_pages.get_selection()
        for index in selected:
            self._database.remove(index)

    def _filter_comm(self):
        """Open the filter window and apply selected filters to the database."""
        filter_window = FiltersWindow(self)
        filter_window.focus_set()
        filter_window.grab_set()
        filter_window.wait_window()

        filters = filter_window.get_results()
        self._database.sort_by(sort_key=lambda x: x.date, filters=filters, reverse=True)

    def _revert_comm(self):
        """Revert the last committed change."""
        self._database.revert()

    def _commit_comm(self):
        """Commit all changes to the database."""
        self._database.commit()

    def _check_saved_committed(self) -> bool:
        """
        Check if the database has uncommitted or unsaved changes. Prompts the user for confirmation.

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

    def _update_buttons(self):
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

    def _load_config(self, filename: str):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                config = json.load(f)
        except IOError:
            mb.showerror("No configuration found", "The program couldn't find the configuration file."
                                                   "\nAn empty one will be created.")
            return
        except json.JSONDecodeError:
            mb.showerror("Malformed configuration", "The program configuration file is malformed."
                                                    "\nAn empty one will be created.")
            return

        try:
            self._templates = config["templates"]
            self._conversions = config["conversions"]
        except KeyError:
            mb.showerror("Malformed configuration", "The program configuration file is malformed."
                                                    "\nAn empty one will be created.")

    def _save_config(self, filename: str):
        config = {
            "conversions": self._conversions,
            "templates": self._templates
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            mb.showerror("Error", f"Could not save the configuration:\n{str(e)}")
