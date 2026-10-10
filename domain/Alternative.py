class Alternative:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def to_dict(self) -> dict:
        return {'name': self.name, 'description': self.description}

    @classmethod
    def from_dict(cls, data: dict) -> 'Alternative':
        return cls(name=data['name'], description=data.get('description', ''))
