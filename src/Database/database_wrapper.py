from src.Database import Database


class DatabaseView(Database):
    """
    Creates a view over a database that enables sorting its entries using arbitrary functions.
    The advantage of this implementation over using raw database is that the order of
    entries is never changed when sorting. Also, no copies of the entries are created,
    unless retrieving the slices.
    """
    def __init__(self, slice_size=10):
        super().__init__()
        self._view = []
        self._slice_size = slice_size  # Indices are zero-based

    def sort_by(self, getter, reverse=False):
        self._view = sorted(
            range(len(self._entries)),
            key=lambda i: getter(self._entries[i]),
            reverse=reverse
        )

    def default_view(self):
        self._view = []

    def get_slice(self, slice_number):
        """Returns only a given slice of data."""
        start = slice_number * self._slice_size
        end = start + self._slice_size

        if start >= len(self._entries):
            return []

        if end > len(self._entries):
            end = len(self._entries)

        if len(self._view) == 0:
            return self._entries[start:end]

        return [self._entries[i] for i in self._view[start:end]]



