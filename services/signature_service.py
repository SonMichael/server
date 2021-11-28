from database import database
from models.signature import Signature


class SignatureService:
    def __init__(self):
        self.connection = database.open()

    def get_by_user_id(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, path FROM signature WHERE user_id = " + str(user_id))

        signatures = []
        for row in cursor.fetchall():
            signature = Signature(id=row[0], path=row[1], user_id=user_id)
            signatures.append(signature)

        return signatures