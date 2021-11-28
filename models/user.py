class User:
    def __init__(self, id=None, name=None, age=None):
        self.id = id
        self.name = name
        self.age = age

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
        }