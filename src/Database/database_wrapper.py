from pathlib import Path
from typing import Callable
from enum import Enum

from src.Database import Database


class Action(Enum):
    NONE = 0  # No action was performed
    LOAD = 1  # Database loading
    PUSH = 2  # Pushing changes (i.e. calling add, remove, edit)
    STATE_CHANGE = 3  # Commiting / reverting changes


class DatabaseView(Database):
    """
    Creates a view over a database that enables sorting its entries using arbitrary functions.
    The advantage of this implementation over using raw database is that the order of
    entries is never changed when sorting. Also, no copies of the entries are created,
    unless retrieving the slices.

    It also employs reactive programming, as classes that depend on the database's data
    can add their own callback that is called every time the database changes state.
    """
    def __init__(self):
        super().__init__()
        self._view = []
        self._subscribers = []
        self._prev_action = Action.NONE

    def sort_by(self, getter, reverse=False):
        self._view = sorted(
            range(len(self._entries)),
            key=lambda i: getter(self._entries[i]),
            reverse=reverse
        )

    def load(self, filename: Path | str, **kwargs):
        super().load(filename, **kwargs)
        self._prev_action = Action.LOAD
        self._call_all()

    def commit(self):
        super().commit()
        self._prev_action = Action.STATE_CHANGE
        self._call_all()

    def revert(self):
        super().revert()
        self._prev_action = Action.STATE_CHANGE
        self._call_all()

    def add(self, transaction):
        super().add(transaction)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def remove(self, index):
        super().remove(index)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def edit(self, index, transaction):
        super().edit(index, transaction)
        if self._prev_action != Action.PUSH:
            self._prev_action = Action.PUSH
            self._call_all()

    def subscribe(self, callback: Callable[[], None]):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def _call_all(self):
        for callback in self._subscribers:
            callback()

    def default_view(self):
        self._view = []

    def __getitem__(self, item):
        if len(self._view) == 0:
            return self._entries[item]

        return [self._entries[i] for i in self._view[item]]

