import os
import pickle


class FaceKind(object):
    Unknown = -1
    Normal = 0
    Missing = 1
    Wanted = 2


class User(object):
    def __init__(self, name, thumbnail, identity, kind=FaceKind.Normal):
        self.name = name
        self.kind = kind
        self.thumbnail = thumbnail
        self.identity = identity

    def make_empty(self):
        self.name = ""
        self.kind = FaceKind.Unknown
        self.thumbnail = ""
        self.identity = -1


class FaceDatabase(object):
    def __init__(self):
        if os.path.exists("user.pickle"):
            self.users = pickle.load(open('user.pickle', 'rb'))
        else:
            self.users = []

    def find_user_by_index(self, index):
        return self.users[index]

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

    def add_new_user(self, name, thumbnail, kind):
        identity = len(self.users)
        self.users.append(User(name, thumbnail, identity, kind))
        return identity

    def remove_user(self, name):
        user = self.find_user_by_name(name)
        removed_identity = user.identity

        user.make_empty()

        return removed_identity
