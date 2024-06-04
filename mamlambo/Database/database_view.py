from pathlib import Path
from typing import Callable, Union

from mamlambo.Database import Database
from mamlambo.Enums.enums import Action


class DatabaseView[T]:
    """
    Creates a view over a database that enables sorting its entries using arbitrary functions.
    The advantage of this implementation over using raw database is that the order of
    entries in the actual database is never changed when sorting. Also, no copies of the
    entries are created, unless retrieving the slices.

    It also employs reactive programming, as classes that depend on the database's data
    can add their own callback that is called every time the database changes state.
    """

    def __init__(self, sort_key, reverse_sort):
        """
        Initialize the DatabaseView with sorting and filtering capabilities.

        :param sort_key: The key function to sort the database entries.
        :param reverse_sort: Boolean indicating whether to sort in reverse order.
        """
        super().__init__()
        self._view: list[int] = []
        self._database = Database[T]()
        self._subscribers: list[Callable[[], None]] = []
        self._prev_action = Action.NONE
        self._saved = False
        self._sort_key = sort_key
        self._reverse = reverse_sort
        self._filters = []

    def __len__(self):
        """Return the number of entries in the view."""
        return len(self._view)

    def __getitem__(self, item) -> Union[T, list[T]]:
        """
        Get a database entry by index or slice.

        :param item: The index or slice to retrieve.
        :return: The entry or list of entries at the specified index or slice.
        """
        if type(item) is int:
            return self._database[self._view[item]]

        return [self._database[i] for i in self._view[item]]

    def sort_by(self, /, sort_key=None, reverse=None, filters=None) -> None:
        """
        Sorts the entries in the database according to the given arguments.
        If any of the arguments is left out, the previously used one will be used.

        :param sort_key: A function that is called on the database entry, returning the value to sort by.
        :param reverse: Whether to reverse the sort order.
        :param filters: A list of filters that all have to return `True` to keep the database entry.
        :return: None
        """
        if sort_key is None:
            sort_key = self._sort_key
        else:
            self._sort_key = sort_key

        if reverse is None:
            reverse = self._reverse
        else:
            self._reverse = reverse

        if filters is not None:
            indices = [i for i in range(len(self._database)) if self._check_filters(self._database[i], filters)]
            self._filters = filters
        else:
            indices = [i for i in range(len(self._database)) if self._check_filters(self._database[i], self._filters)]

        self._view = sorted(
            indices,
            key=lambda i: sort_key(self._database[i]),
            reverse=reverse
        )
        self._prev_action = Action.STATE_CHANGE
        self._call_all()

    def dump(self, filename: Path, /, delimiter: str = ',') -> None:
        """
        Dump the database transactions into a CSV or JSON file.

        :param filename: The path to the file to write to.
        :param delimiter: The delimiter to use in the CSV file.
        :return: None
        """
        self._database.dump(filename, delimiter)
        self._saved = True

    def load(self, filename: Path | str, line_parser: Callable[[list[str]], T], /, delimiter=","):
        """
        Load transactions from a file into the database and sort them.

        :param filename: The path to the file to load.
        :param line_parser: Parses the file to the database representation.
        :param delimiter: The delimiter used in the file.
        :return: None
        """
        self._database.load(filename, line_parser, delimiter)
        self._prev_action = Action.LOAD
        self._saved = True
        self.sort_by()

    def commit(self):
        """
        Process all pending commits to the database and update the view.

        :return: None
        """
        self._database.commit()
        self._prev_action = Action.STATE_CHANGE
        self._saved = False
        self.sort_by()

    def revert(self):
        """
        Revert the last commit in the database and update the view.

        :return: None
        """
        self._database.revert()
        self._prev_action = Action.STATE_CHANGE
        self._saved = False
        self.sort_by()

    def add(self, transaction):
        """
        Schedule a transaction to be added to the database and notify subscribers.

        :param transaction: The Transaction object to add.
        :return: None
        """
        self._database.add(transaction)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def remove(self, index):
        """
        Schedule a transaction to be removed from the database by index and notify subscribers.

        :param index: The index of the transaction to remove.
        :return: None
        """
        if len(self._view) > 0:
            index = self._view[index]
        self._database.remove(index)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def edit(self, index, transaction):
        """
        Schedule a transaction to be updated in the database by index and notify subscribers.

        :param index: The index of the transaction to update.
        :param transaction: The new Transaction object to replace the old one.
        :return: None
        """
        if len(self._view) > 0:
            index = self._view[index]
        self._database.edit(index, transaction)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def subscribe(self, callback: Callable[[], None]):
        """
        Subscribe a callback to be called whenever the database changes state.

        :param callback: A callable function to be called on database state change.
        :return: None
        """
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            callback()  # To let the new subscriber know the current state

    def is_saved(self) -> bool:
        """
        Check if the current state of the database is saved.

        :return: True if the database is saved, False otherwise.
        """
        return self._saved

    def all_committed(self) -> bool:
        """
        Check if all changes are committed to the database.

        :return: True if there are no pending commits, False otherwise.
        """
        return len(self._database.get_commits()) == 0

    def can_revert(self):
        """
        Check if there is a commit to revert.

        :return: True if there is a commit to revert, False otherwise.
        """
        return len(self._database.get_history()) > 0

    def _call_all(self):
        """Call all subscriber callbacks to notify them of a state change."""
        for callback in self._subscribers:
            callback()

    @staticmethod
    def _check_filters(entry: T, filters: list[Callable[[T], bool]]) -> bool:
        """
        Check if a transaction passes all filters.

        :param entry: The T entry to check.
        :param filters: A list of callables that return True if the transaction matches the filter.
        :return: True if the transaction passes all filters, False otherwise.
        """
        for fil in filters:
            if not fil(entry):
                return False

        return True
