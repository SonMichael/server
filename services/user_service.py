from database import database
from models.user import User


class UserService:
    def __init__(self):
        self.connection = database.open()

    def get_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
        rows = cursor.fetchall()
        return rows

    def get_user_by_id(self, id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, username, password, age FROM user WHERE id = " + str(id))
        row = cursor.fetchone()

        if row is None:
            return None
        return User(id=row[0], name=row[1], age=row[3])
