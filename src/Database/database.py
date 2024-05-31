import csv
from collections import deque
from typing import Callable
from pathlib import Path

from src.Transactions import Transaction


class Database:
    def __init__(self):
        """Initialize the Database with empty lists for entries and commits, and an empty deque for free indices."""
        self._entries: list[Transaction] = []
        self._commits = []
        self._free_indices = deque()
        self._history = deque(maxlen=3)

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def load(self, filename: Path | str, /, delimiter: str = ',') -> None:
        """
        Load transactions from a CSV file into the database.

        :param filename: The path to the CSV file to load.
        :param delimiter: The delimiter used in the CSV file.
        """
        # In case we load an already loaded database
        self._entries = []
        self._commits = []
        self._free_indices = deque()
        self._history = deque(maxlen=3)

        with open(filename, 'r', encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                self._entries.append(Transaction.parse(row))

    def dump(self, filename: Path | str, /, delimiter: str = ',') -> None:
        """
        Dump the database transactions into a CSV file.

        :param filename: The path to the CSV file to write to.
        :param delimiter: The delimiter to use in the CSV file.
        """
        with open(filename, 'w', encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerows(map(lambda e: e.dump(), self._entries))

    def commit(self):
        """Process all pending commits to the database and store them in history."""
        commit_data = []
        for commit in self._commits:
            commit_data.append(self._handle_commit(commit))

        self._history.appendleft(commit_data)  # Store the commit data in history
        self._commits = []  # Clear the commits after processing

    def revert(self):
        """Revert the last commit."""
        if not self._history:
            raise Exception("No commit to revert.")
        last_commit_data = self._history.popleft()
        for commit in reversed(last_commit_data):
            self._undo_commit(commit)

    def all_commited(self):
        return len(self._commits) == 0

    def can_revert(self):
        return len(self._commits) > 0

    def select(self, filters: list[Callable[[Transaction], bool]]) -> list[Transaction]:
        """
        Select transactions that match all the given filters.

        :param filters: A list of callables that return True if the transaction matches the filter.
        :return: A list of Transactions that match all filters.
        """
        selected = []
        for transaction in self._entries:
            if self._check_filters(transaction, filters):
                selected.append(transaction)

        return selected

    def add(self, transaction: Transaction):
        """
        Schedule a transaction to be added to the database.

        :param transaction: The Transaction object to add.
        """
        commit = {
            "action": "add",
            "value": transaction
        }
        self._commits.append(commit)

    def remove(self, index: int):
        """
        Schedule a transaction to be removed from the database by index.

        :param index: The index of the transaction to remove.
        """
        commit = {
            "action": "remove",
            "index": index
        }
        self._commits.append(commit)

    def update(self, index: int, transaction: Transaction):
        """
        Schedule a transaction to be updated in the database.

        :param index: The index of the transaction to update.
        :param transaction: The new Transaction object to replace the old one.
        """
        commit = {
            "action": "update",
            "index": index,
            "value": transaction
        }
        self._commits.append(commit)

    def _handle_commit(self, commit: dict) -> dict:
        """
        Handle a single commit action.

        :param commit: A dictionary representing the commit to handle.
        """
        match commit["action"]:
            case "add":
                if len(self._free_indices) > 0:
                    index = self._free_indices.popleft()
                    self._entries[index] = commit["value"]
                    commit["index"] = len(self._entries) - 1
                else:
                    self._entries.append(commit["value"])

            case "remove":
                index = commit["index"]
                commit["old_value"] = self._entries[index]
                self._entries[index] = None
                self._free_indices.append(index)

            case "update":
                index = commit["index"]
                commit["old_value"] = self._entries[index]
                self._entries[index] = commit["value"]

        return commit

    def _undo_commit(self, commit: dict) -> None:
        """Undo a single commit action."""
        match commit["action"]:
            case "add":
                # Find the transaction to remove
                index = commit["index"]
                if index == len(self._entries) - 1:
                    self._entries.pop()
                else:
                    self._entries[index] = None
                    self._free_indices.append(index)

            case "remove":
                # Restore the removed transaction
                index = commit["index"]
                transaction = commit["old_value"]
                if index >= len(self._entries):
                    self._entries.append(transaction)
                self._entries[index] = transaction
                self._free_indices.remove(index)

            case "update":
                # Revert to the previous transaction
                index = commit["index"]
                transaction = commit["old_value"]
                self._entries[index] = transaction

    @staticmethod
    def _check_filters(transaction: Transaction, filters: list[Callable[[Transaction], bool]]) -> bool:
        """
        Check if a transaction passes all filters.

        :param transaction: The Transaction to check.
        :param filters: A list of callables that return True if the transaction matches the filter.
        :return: True if the transaction passes all filters, False otherwise.
        """
        for fil in filters:
            if not fil(transaction):
                return False

        return True
