import tkinter as tk
from tkinter import ttk
from typing import Literal


class ButtonRowFrame(tk.Frame):
    """
    Represents a row of buttons.
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._buttons = dict()
        self._last_column = 0

    def __getitem__(self, item):
        return self._buttons[item]

    def add_button(self, label="", icon=None, command=None, side: Literal["left", "right", "top", "bottom"] = "left"):
        button = ttk.Button(self, text=label, image=icon, command=command)
        button.pack(side=side)
        self._buttons[label.lower()] = button

    def enable_all(self):
        for button in self._buttons.values():
            button["state"] = "normal"

    def disable_all(self):
        for button in self._buttons.values():
            button["state"] = "disabled"
