from tinydb import TinyDB, Query
from google.cloud import storage

import user_database

storage_client = storage.Client()
bucket_name = "autotennis"
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob("bookings")

db = TinyDB("./bookingDB.json")
Booking = Query()

def boot():
    blob.download_to_filename("./bookingDB.json")

def is_in_db(email, event_url):
    if db.search(Booking.email == email and Booking.event_url == event_url) == []:
        return False
    else:
        return True

def add_entry(email, event_url, type):
    db.insert({'email': email, 'event_url': event_url, 'type': type})
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