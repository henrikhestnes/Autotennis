from tinydb import TinyDB, Query
import custom_logging
import requests

from google.cloud import storage

storage_client = storage.Client()
bucket_name = "autotennis"
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob("users")

db = TinyDB("./userDB.json")
User = Query()

def sync():
    blob.download_to_filename("./userDB.json")

def is_in_db(email):
    if db.search(User.email == email) == []:
        return False
    else:
        return True

def add_entry(email, password, vikar_id):
    if not is_valid_user(email, password):
        custom_logging.info(f'Invalid user: {email}')
        return
    db.insert({'email': email, 'password': password, 'vikar_id': vikar_id})
    blob.upload_from_filename('./userDB.json')

def update(email, password, vikar_id):
    if not is_valid_user(email, password):
        custom_logging.info(f'Invalid user: {email}')
        return
    db.update({'email': email, 'password': password, 'vikar_id': vikar_id}, User.email == email)
    blob.upload_from_filename('./userDB.json')

def get_entry(email):
    return db.search(User.email == email)[0]

def get_registered_emails():
    return [user['email'] for user in db]

def is_valid_user(email, password):
    homepage_url = "https://www.ntnuitennis.no/index.php?lang=no"
    login_values = {'email': email,
                    'password': password,
                    'lang': "no",
                    'rememberme': "on"}
    s = requests.Session()
    r = s.post(url=homepage_url, data=login_values)
    
    login_string = "Du er nå innlogget som"
    if login_string not in r.text:
        return False
    return True
