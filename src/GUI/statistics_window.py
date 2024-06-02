import tkinter as tk
from tkinter import ttk

from src.Database.database_wrapper import DatabaseView


class StatisticsWindow(tk.Toplevel):
    def __init__(self, master, database: DatabaseView):
        super().__init__(master)
        self.database = database



