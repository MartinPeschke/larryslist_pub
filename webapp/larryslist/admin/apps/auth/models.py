from jsonclient import Mapping, TextField

__author__ = 'Martin'


class AdminUser(Mapping):
    token = TextField()
    name = TextField()
    country = TextField()

def getStandardUser():
    return AdminUser(token='1', name = 'feeder1', country='us')