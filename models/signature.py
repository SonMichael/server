class Signature:
    def __init__(self, id=None, user_id=None, path=None):
        self.id = id
        self.user_id = user_id
        self.path = path

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "path": self.path,
        }