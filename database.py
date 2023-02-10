from tinydb import TinyDB, Query
from tinydb_appengine.storages import EphemeralJSONStorage
# from google.cloud import storage

# storage_client = storage.Client()
# bucket = storage_client.bucket("user_bucket")
# blob = bucket.blob("user_blob")

db = TinyDB("./userDB.json", storage=EphemeralJSONStorage)
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

def get_registered_emails():
    return [user['email'] for user in db]