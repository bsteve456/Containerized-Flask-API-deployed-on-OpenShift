# Temporary in-memory storage (no database yet)
tasks_db = {}
next_id = 1

class Task:
    def __init__(self, id, title):
        self.id = id
        self.title = title
    
    def to_dict(self):
        return {'id': self.id, 'title': self.title}