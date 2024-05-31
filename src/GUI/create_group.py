import tkinter as tk
from tkinter import ttk


class ManageGroupsWindow(tk.Toplevel):
    def __init__(self, master, groups):
        super().__init__(master)
        self.title('Manage Groups')
        self.groups = groups
        self.list = None

        self.setup_list()
        self.setup_buttons()

    def setup_list(self):
        pass

    def setup_buttons(self):
        pass
        
        
        
        
        
        
        