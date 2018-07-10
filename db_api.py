from config import *


class DBApi:
    def __init__(self, db_name):
        self.db = dbs[db_name]()

    def search_db(self):
        return self.db.search()


if __name__ == '__main__':
    a = DBApi("movies")
    pass
