from database import database
from models.user import User


class UserService:
    def __init__(self):
        self.connection = database.open()

    def get_all_users(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, username, password, age FROM user ORDER BY id")

        users = []
        for row in cursor.fetchall():
            user = User(id=row[0], name=row[1], age=row[2])
            users.append(user)

        return users

    def get_user_by_id(self, id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, username, password, age FROM user WHERE id = " + str(id))
        row = cursor.fetchone()

        if row is None:
            return None
        return User(id=row[0], name=row[1], age=row[3])
