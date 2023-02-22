from tinydb import TinyDB, Query
from urllib.parse import urlparse, parse_qs
from google.cloud import storage

import user_database

storage_client = storage.Client()
bucket_name = "autotennis"
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob("bookings")

db = TinyDB("./bookingDB.json")
Booking = Query()

def sync():
    blob.download_to_filename("./bookingDB.json")

def is_in_db(email, event_url):
    if db.search((Booking.email == email) & (Booking.event_url == event_url)) == []:
        return False
    else:
        return True

def is_recurring(email, event_url):
    if db.search((Booking.email == email) & (Booking.event_url == event_url) & (Booking.recurring == True)) == []:
        return False
    else:
        return True

def add_entry(email, event_url, recurring, type):
    if not is_valid_url(event_url):
        return
    db.insert({'email': email, 'event_url': event_url, 'recurring': recurring,'type': type})
    blob.upload_from_filename('./bookingDB.json')

def remove_entry(email, event_url):
    db.remove(Booking.email == email and Booking.event_url == event_url)
    blob.upload_from_filename('./bookingDB.json')

def get_all_entries():
    return db.all()

def get_active_bookings_per_user():
    active_bookings = {user: [] for user in user_database.get_registered_emails()}
    for booking in get_all_entries():
        active_bookings[booking['email']].append(booking['event_url'])
    return active_bookings

def is_valid_url(event_url):
    url_parsed = urlparse(event_url)
    query = parse_qs(url_parsed.query)
    if url_parsed.netloc != 'www.ntnuitennis.no':
        return False
    required_query = ['timeid', 'spilletid']
    for q in required_query:
        if q not in query.keys():
            return False
    allowed_query = ['timeid', 'spilletid', 'lang']
    for q in query:
        if q not in allowed_query:
            return False
    return True