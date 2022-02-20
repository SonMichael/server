class SignatureRequest:
    def __init__(self, id=None, user_id=None, username=None, path=None, document_path=None, similarity=None, created_date=None, is_accepted=None, most_genuine_signature=None):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.path = path
        self.document_path = document_path
        self.similarity = similarity
        self.created_date = created_date
        self.is_accepted = is_accepted
        self.most_genuine_signature = most_genuine_signature

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "path": self.path,
            "document_path": self.document_path,
            "similarity": self.similarity,
            "created_date": self.created_date,
            "is_accepted": self.is_accepted,
            "most_genuine_signature": self.most_genuine_signature,
        }