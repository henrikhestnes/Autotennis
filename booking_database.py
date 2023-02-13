from tinydb import TinyDB, Query
import pytz
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from dateutil.parser import parse

db = TinyDB("./bookingDB.json")
Booking = Query()

def add_entry(email, event_url):
    
    event_time = parse(parse_qs(urlparse(event_url).query)['spilletid'][0])
    event_timezone = pytz.timezone("Europe/Oslo")
    event_time = event_timezone.localize(event_time)
    registration_time = event_time - timedelta(hours=72)
    utc_registration_time = registration_time.astimezone(pytz.UTC)
    db.insert({'email': email, "utc_registration_time": utc_registration_time ,'event_url': event_url})

def remove_entry(email, event_url):
    db.remove(Booking.email == email and Booking.event_url == event_url)

def get_all_entries():
    return db


#HELPER FUNCTIONS
def is_valid_url(event_url, session):
    r = session.get(event_url)
    if 'ERROR' in r.text:
        return False
    return True

def time_diff_seconds(time_a, time_b):
    return (time_a - time_b).total_seconds()