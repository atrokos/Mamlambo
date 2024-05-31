import tkinter as tk
from tkinter import filedialog as fd
import tkinter.messagebox as mb


from src.Database.database_wrapper import DatabaseView
from src.GUI.about_window import AboutWindow
from src.GUI.button_row import ButtonRow
from src.GUI.transaction_view import TransactionTreeView


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Mamlambo")  # Set the window title
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self._left_ribbon = None
        self._right_ribbon = None
        self.treeview = None
        self.database = None

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
        file_menu.add_command(label="Save as", command=self.open_session)
        file_menu.add_command(label='Exit', command=self.destroy)

        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="CSV")
        options_menu.add_command(label="Commits")

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.display_about)

        menubar.add_cascade(label='File', menu=file_menu)
        menubar.add_cascade(label='Options', menu=options_menu)
        menubar.add_cascade(label='Help', menu=help_menu)
        self.config(menu=menubar)  # Set the menubar for the main window

    def new_session(self):
        if self.database is not None and not self.database.all_commited():
            answer = mb.askyesno("Confirmation", "Not all changes were commited, do you want to continue?")
            if not answer:
                return

        self.database = DatabaseView()
        self._left_ribbon.enable_all()
        self.update_buttons()

    def open_session(self):
        if self.database is not None and not self.database.all_commited():
            answer = mb.askyesno("Confirmation", "Not all changes were commited, do you want to continue?")
            if not answer:
                return

        filename = fd.askopenfilename()
        self.database = DatabaseView()
        self.database.load(filename)
        self.treeview.populate_tree(self.database.get_slice(0))
        self._left_ribbon.enable_all()
        self.update_buttons()

    def save_session(self):
        if self.database is None:
            mb.showinfo("Empty database", "No database was created.")
            return

        if not self.database.all_commited():
            answer = mb.askyesno("Confirmation", "Not all changes were commited, do you want to continue?")
            if not answer:
                return

        filename = fd.asksaveasfilename()
        self.database.dump(filename)

    def display_about(self):
        AboutWindow(self, "0.1.0 alpha")

    def setup_ribbon(self):
        self._left_ribbon = ButtonRow(self)
        self._left_ribbon.grid(row=0, column=0, sticky='nsw')

        self._left_ribbon.add_button("Add", command=self.nothing)
        self._left_ribbon.add_button("Edit", command=self.nothing)
        self._left_ribbon.add_button("Remove", command=self.nothing)
        self._left_ribbon.add_button("Filter", command=self.nothing)
        self._left_ribbon.disable_all()

        self._right_ribbon = ButtonRow(self)
        self._right_ribbon.grid(row=0, column=1, sticky="nse")

        self._right_ribbon.add_button("Revert", command=self.nothing)
        self._right_ribbon.add_button("Commit", command=self.nothing)

    def nothing(self, event=None):
        pass

    def add_transaction(self):
        # TODO Create a new window where user inputs transaction info
        pass

    def setup_transaction_view(self):
        self.treeview = TransactionTreeView(self)
        self.treeview.grid(row=1, column=0, columnspan=10, pady=(5, 0), sticky='nsew')

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
