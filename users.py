from flask_login import UserMixin
class User(UserMixin):
    def __init__(self,user_document):
        self.id = user_document['_id']
        self.name = user_document['name']
        self.username = user_document['username']
        self.email = user_document['email']