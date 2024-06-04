import tkinter as tk


class AboutWindow(tk.Toplevel):
    def __init__(self, parent, ver: str):
        tk.Toplevel.__init__(self, parent)
        self.version = ver

        self.resizable(False, False)
        self.geometry('200x200')
        self.title('About')
        tk.Label(self, text='Mamlambo', font=('Arial', 14)
                 ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(self, text=f"Version {self.version}", font=('Arial', 12)
                 ).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)




