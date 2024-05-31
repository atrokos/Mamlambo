import tkinter as tk
from tkinter import ttk

from src.GUI.about_window import AboutWindow
from src.GUI.button_row import ButtonRow


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Mamlambo")  # Set the window title
        self.geometry("800x600")
        self.resizable(False, False)
        self.setup_menu()
        self.setup_ribbon()

    def setup_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='New', command=self.new_session)
        file_menu.add_command(label="Open", command=self.open_session)
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
        pass

    def open_session(self):
        pass

    def display_about(self):
        AboutWindow(self, "0.1.0 alpha")

    def setup_ribbon(self):
        row = ButtonRow(self)
        row.grid(row=0, column=0, sticky='nsew')

        row.add_button("Add", command=self.nothing)
        row.add_button("Edit", command=self.nothing)
        row.add_button("Remove", command=self.nothing)

    def nothing(self, event=None):
        pass


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
