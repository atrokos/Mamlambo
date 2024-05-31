import tkinter as tk
from tkinter import ttk
from typing import Literal


class ButtonRow(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._buttons = dict()
        self._last_column = 0

    def __getitem__(self, item):
        return self._buttons[item]

    def add_button(self, label="", icon=None, command=None, side: Literal["left", "right", "top", "bottom"] = "left"):
        button = ttk.Button(self, text=label, image=icon, command=command)
        button.pack(side=side)
        self._buttons[label] = button

    def add_separator(self, side: Literal["left", "right", "top", "bottom"] = "left"):
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=side, expand=True, fill=tk.BOTH, padx=5)

    def _next_column(self):
        self._last_column += 1
        return self._last_column
