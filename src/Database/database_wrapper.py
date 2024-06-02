from pathlib import Path
from typing import Callable
from enum import Enum

from src.Database import Database


class Action(Enum):
    NONE = 0  # No action was performed
    LOAD = 1  # Database was loaded
    PUSH = 2  # Pushing changes (i.e. calling add, remove, edit)
    STATE_CHANGE = 3  # Commiting / reverting changes


class DatabaseView(Database):
    """
    Creates a view over a database that enables sorting its entries using arbitrary functions.
    The advantage of this implementation over using raw database is that the order of
    entries in the actual database is never changed when sorting. Also, no copies of the
    entries are created, unless retrieving the slices.

    It also employs reactive programming, as classes that depend on the database's data
    can add their own callback that is called every time the database changes state.
    """
    def __init__(self, sort_key, reverse_sort):
        super().__init__()
        self._view = []
        self._subscribers = []
        self._prev_action = Action.NONE
        self._saved = False
        self._sort_key = sort_key
        self._reverse = reverse_sort
        self._filters = []

    def __len__(self):
        return len(self._view)

    def sort_by(self, /, sort_key=None, reverse=None, filters=None) -> None:
        """
        Sorts the entries in the database according to the given arguments.
        If any of the arguments is left out, the previously used one will be used.
        :param sort_key: A function that is called on the database entry, returning the value to sort by.
        :param reverse: Whether to reverse the sort order.
        :param filters: A list of filters that all have to return `True` to keep the database entry.
        :return:
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
            indices = [i for i in range(len(self._entries)) if Database._check_filters(self._entries[i], filters)]
            self._filters = filters
        else:
            indices = [i for i in range(len(self._entries)) if Database._check_filters(self._entries[i], self._filters)]

        self._view = sorted(
            indices,
            key=lambda i: sort_key(self._entries[i]),
            reverse=reverse
        )
        self._prev_action = Action.STATE_CHANGE
        self._call_all()

    def dump(self, filename: Path, /, delimiter: str = ',') -> None:
        super().dump(filename, delimiter)
        self._saved = True

    def load(self, filename: Path | str, /, delimiter=","):
        super().load(filename, delimiter)
        self._prev_action = Action.LOAD
        self._saved = True
        self.sort_by()

    def commit(self):
        super().commit()
        self._prev_action = Action.STATE_CHANGE
        self._saved = False
        self.sort_by()

    def revert(self):
        super().revert()
        self._prev_action = Action.STATE_CHANGE
        self._saved = False
        self.sort_by()

    def add(self, transaction):
        super().add(transaction)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def remove(self, index):
        if len(self._view) > 0:
            index = self._view[index]
        super().remove(index)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def edit(self, index, transaction):
        if len(self._view) > 0:
            index = self._view[index]
        super().edit(index, transaction)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def subscribe(self, callback: Callable[[], None]):
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            callback()  # To let the new subscriber know the current state

    def _call_all(self):
        for callback in self._subscribers:
            callback()

    def default_view(self):
        self._view = []

    def is_saved(self):
        return self._saved

    def __getitem__(self, item):
        if len(self._view) == 0:
            return self._entries[item]

        if type(item) is int:
            return self._entries[self._view[item]]

        return [self._entries[i] for i in self._view[item]]

