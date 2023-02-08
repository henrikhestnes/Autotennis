from tinydb import TinyDB, Query

db = TinyDB('./userDB.json')
User = Query()

def is_in_db(email):
    if db.search(User.email == email) == []:
        return False
    else:
        return True

def add_entry(email, password, vikar_id):
    db.insert({'email': email, 'password': password, 'vikar_id': vikar_id})

def update(email, password, vikar_id):
    db.update({'email': email, 'password': password, 'vikar_id': vikar_id}, User.email == email)

def get_entry(email):
    return db.search(User.email == email)[0]