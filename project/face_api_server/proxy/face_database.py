import os
import pickle


class User(object):
    def __init__(self, name, thumbnail, identity):
        self.name = name
        self.thumbnail = thumbnail
        self.identity = identity


class FaceDatabase(object):
    def __init__(self):

        if os.path.exists("user.pickle"):
            self.users = pickle.load(open('user.pickle', 'rb'))
        else:
            self.users = []

    def find_user_by_index(self, index):
        return self.people[index]

    def find_user_by_name(self, name):
        for user in self.users:
            if user.name == name:
                return user

        return None

    def is_exist(self, name):
        for user in self.users:
            if user.name == name:
                return True

        return False

    def add_new_user(self, name, thumbnail):
        identity = len(self.users)
        self.users.append(User(name, thumbnail, identity))
        return identity
