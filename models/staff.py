class Staff:
    def __init__(self, id=None, name=None, age=None, is_supervisor=0):
        self.id = id
        self.name = name
        self.age = age
        self.is_supervisor = is_supervisor

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "is_supervisor": self.is_supervisor,
        }