from src.Database import Database


class DatabaseView(Database):
    def __init__(self):
        super().__init__()
        self._view = []
        self._per_page = 10
        self._page_no = 1

    def sort_by(self, getter):
        self._view = sorted(
            range(len(self._entries)),
            key=lambda i: getter(self._entries[i])
        )

    def default_view(self):
        self._view = []

    def get_page(self, page_number):
        pass

    def next_page(self):
        pass

    def previous_page(self):
        pass

