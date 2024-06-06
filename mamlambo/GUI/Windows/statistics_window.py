import datetime
import tkinter as tk
from tkinter import ttk
import math
from collections import Counter

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mamlambo.Database.database_view import DatabaseView
matplotlib.use("TkAgg")


def unzip(l: list):
    """Unzips the list of tuples to two lists."""
    if len(l) == 0:
        return [], []

    unzipped = list(zip(*l))
    return list(unzipped[0]), list(unzipped[1])


class StatisticsWindow(tk.Toplevel):
    """Renders the statistics window."""
    def __init__(self, master, database: DatabaseView):
        super().__init__(master)
        self.title("Statistics")
        self.resizable(False, False)

        data, group_data, time_data = self._prepare_data(database)
        title_text = f"Statistics from {data['min_date']} to {data['max_date']}"
        ttk.Label(self, text=title_text, font=("Arial", 18)
                  ).grid(column=0, row=0, columnspan=2, sticky="nsew", padx=5, pady=(5, 10))
        StatisticsDataFrame(self, data).grid(row=1, column=0, sticky="nsew", padx=5, pady=(5, 10))
        self.plot_line(time_data, data["currency"])
        self.plot_pies(group_data["incomes"], group_data["expenses"])

    def plot_line(self, time_data, currency: str):
        dates = time_data["dates"]
        totals = time_data["totals"]

        fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))
        fig.set_facecolor("#f0f0f0")

        ax1.set_title("Balance over time")
        ax1.set_xlabel("Date")
        ax1.set_ylabel(f"Balance [{currency}]")

        ax1.plot(dates, totals)
        ax1.tick_params(axis='x', labelrotation=70)
        fig.tight_layout()

        # Embed the figure as a Tkinter widget
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0)

    def plot_pies(self, incomes: Counter, expenses: Counter):
        # Data for the "Incomes" pie chart
        inc_values, inc_labels = self.prepare_pie_data(incomes)

        # Data for the "Expenses" pie chart
        exp_values, exp_labels = self.prepare_pie_data(expenses)

        # Create the figure and subplots
        fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(5, 5))
        fig.set_facecolor("#f0f0f0")

        # Plot the "Incomes" pie chart
        ax1.pie(inc_values, labels=inc_labels, startangle=90, labeldistance=1.1)
        ax1.set_title('Incomes')

        # Plot the "Expenses" pie chart
        ax2.pie(exp_values, labels=exp_labels, startangle=90, labeldistance=1.1),
        ax2.set_title('Expenses')

        # Embed the figure as a Tkinter widget
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, rowspan=3, column=1)

    def _prepare_data(self, database: DatabaseView):
        """Runs through the data, collecting needed statistics from it."""
        data, group_data = self._init_dicts()
        dates_totals: list[tuple[datetime.date, float]] = []
        total_balance = 0

        for i in range(len(database)):
            curr_transaction = database[i]
            amount = curr_transaction.amount

            if amount > data["max"][0]:
                data["max"] = (amount, curr_transaction.title)
            elif amount < data["min"][0]:
                data["min"] = (amount, curr_transaction.title)

            if amount > 0:
                group_data["incomes"][curr_transaction.group.name] += amount
            elif amount < 0:
                # Subtracting so that the Counter returns the group with the biggest expenses first
                group_data["expenses"][curr_transaction.group.name] -= amount

            if data["min_date"] is None or data["min_date"] > curr_transaction.date:
                data["min_date"] = curr_transaction.date
            if data["max_date"] is None or data["max_date"] < curr_transaction.date:
                data["max_date"] = curr_transaction.date

            if data["currency"] is None:
                data["currency"] = curr_transaction.currency

            total_balance += amount
            dates_totals.append((curr_transaction.date, total_balance))

        if len(database) != 0:
            data["avg"] = total_balance / len(database)

        time_data = self._get_time_data(dates_totals)  # Convert the data in time to the required representation

        return data, group_data, time_data

    @staticmethod
    def _init_dicts():
        data = {
            "max": (-math.inf, None),
            "min": (math.inf, None),
            "avg": 0.0,
            "min_date": None,
            "max_date": None,
            "currency": None
        }
        group_data = {
            "incomes": Counter(),
            "expenses": Counter()
        }
        return data, group_data

    @staticmethod
    def _get_time_data(totals_dates: list[tuple[datetime.date, float]]):
        # Converts the list of tuples to a dictionary
        time_data = {
            "totals": [],
            "dates": []
        }

        dates, totals = unzip(totals_dates)
        time_data["dates"] = dates
        time_data["totals"] = totals
        return time_data

    @staticmethod
    def prepare_pie_data(data: Counter, n=4):
        # Selects up to `n` largest groups from the data, putting the rest in a category called "Rest"
        rest_sum = None

        if len(data) > n:
            n_largest_incomes = data.most_common()[:n]
            rest_sum = sum(map(lambda x: x[1], data.most_common()[n:]))
        else:
            n_largest_incomes = data.most_common()

        group_name, group_value = unzip(n_largest_incomes)
        if rest_sum is not None:
            group_value.append(rest_sum)
            group_name.append("Rest")

        return group_value, group_name


class StatisticsDataFrame(tk.Frame):
    """
    Displays the statistics in numbers.
    """
    def __init__(self, master, data):
        super().__init__(master)
        self.data = data
        self._setup_labels()

    def _setup_labels(self):
        currency = self.data["currency"]

        self._create_stats_labels("Maximum amount:", self.data['max'][0], currency, self.data['max'][1])
        self._create_stats_labels("Minimum amount:", self.data['min'][0], currency, self.data['min'][1])
        self._create_stats_labels("Average amount:", self.data['avg'], currency)

    def _create_stats_labels(self, stat_type: str, amount: float, currency: str, title: str = None):
        """
        Creates multiple labels in the format
        <Stat_type> <Amount> <Currency> [Title]
        """
        currency_text = "{:.2f} {}".format(amount, currency)

        ttk.Label(self, text=stat_type, font="bold"
                  ).grid(row=self._new_row(), column=0, sticky="nsw", padx=5, pady=(5, 10))
        ttk.Label(self, text=currency_text, font="bold"
                  ).grid(row=self._curr_row(), column=1, sticky="nsw", padx=5, pady=(5, 10))
        if title is not None:
            ttk.Label(self, text=title, font="bold"
                     ).grid(row=self._curr_row(), column=2, sticky="nsw", pady=(5, 10))

    def _new_row(self):
        return self.grid_size()[1]

    def _curr_row(self):
        return self.grid_size()[1] - 1
