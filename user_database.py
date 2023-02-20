from tinydb import TinyDB, Query

from google.cloud import storage

storage_client = storage.Client()
bucket_name = "autotennis"
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob("users")

db = TinyDB("./userDB.json")
User = Query()

def boot():
    blob.download_to_filename("./userDB.json")

def is_in_db(email):
    if db.search(User.email == email) == []:
        return False
    else:
        return True

def add_entry(email, password, vikar_id):
    db.insert({'email': email, 'password': password, 'vikar_id': vikar_id})
    blob.upload_from_filename('./userDB.json')

def update(email, password, vikar_id):
    db.update({'email': email, 'password': password, 'vikar_id': vikar_id}, User.email == email)
    blob.upload_from_filename('./userDB.json')

def get_entry(email):
    return db.search(User.email == email)[0]

def get_registered_emails():
    return [user['email'] for user in db]