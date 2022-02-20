from database import database
from models.staff import Staff


class StaffService:
    def __init__(self):
        self.connection = database.open()

    def login(self, username, password):
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT id, username, password, age, is_supervisor FROM staff WHERE username = '{0}' AND password = '{1}';
        """.format(username, password))
        row = cursor.fetchone()

        if row is None:
            return None
        return Staff(id=row[0], name=row[1], age=row[3], is_supervisor=row[4])
