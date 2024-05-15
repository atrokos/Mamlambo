import sqlite3


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, filename: str):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def add_transaction(self):