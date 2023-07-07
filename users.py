from flask_login import UserMixin
class User(UserMixin):
    def __init__(self,user_document):
        self.id = user_document['_id']
        self.name = user_document['name']
        self.username = user_document['username']
        self.email = user_document['email']
        self.__password = user_document['password']

class User_info(User):
    def __init__(self, user_document):
        super().__init__(user_document)
        try:
            self.image = user_document['image']
            self.about = user_document['about']
            self.company = user_document['company']
            self.job = user_document['job']
            self.country = user_document['country']
            self.address = user_document['address']
            self.phone = user_document['phone']
            self.twitter = user_document['twitter']
            self.facebook = user_document['facebook']
            self.instagram = user_document['instagram']
            self.linkedin = user_document['linkedin']
            self.github = user_document['github']
        except:
            self.image = ""
            self.about = ""
            self.company = ""
            self.job = ""
            self.country = ""
            self.address = ""
            self.phone = ""
            self.twitter = ""
            self.facebook = ""
            self.instagram = ""
            self.linkedin = "" 
            self.github = ""
        
