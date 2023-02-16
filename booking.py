import requests
import threading
import time, pytz
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from dateutil.parser import parse
import user_database
import booking_database

confirmation_str = "Kode for tilgang til bygget:"

def boot():
    for booking in booking_database.get_all_entries():
        email = booking['email']
        event_url = booking['event_url']
        t = threading.Thread(target=book, args=(email, event_url))
        t.start()
        print(f"RESTARTING THREAD {email} FOR {booking}")

def book(email, event_url):
    if not sanity_check_good(email, event_url):
        booking_database.remove_entry(email, event_url)
        return
    
    s = requests.Session()

    user = user_database.get_entry(email)
    log_in(user, s)

    registration_url = get_registration_url(event_url, user['vikar_id'])

    event_time = parse(parse_qs(urlparse(event_url).query)['spilletid'][0])
    event_timezone = pytz.timezone("Europe/Oslo")
    event_time = event_timezone.localize(event_time)
    registration_time = event_time - timedelta(hours=72)
    utc_registration_time = registration_time.astimezone(pytz.UTC)

    response = s.get(event_url)
    registration_time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))

    if registration_time_diff > 0:
        schedule_booking(email, event_url, registration_url, utc_registration_time, s)
    else:
        monitor_full_event(email, registration_url, s)

    booking_database.remove_entry(email, event_url)
    print(f"{email} FOR {event_time} EXITING")


def schedule_booking(email, event_url, registration_url, utc_registration_time, session):
    response = session.get(event_url)
    registration_time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
    while registration_time_diff > 5:
        response = session.get(event_url)
        registration_time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
        print(f"{email} for {utc_registration_time + timedelta(hours=72)} sleeping {registration_time_diff/2} seconds")
        time.sleep(registration_time_diff/2)

    response = session.get(registration_url)
    while confirmation_str not in response.text:
        registration_time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
        if registration_time_diff < -60:
            break
        time.sleep(0.05) #0.05 second sleep to avoid ddos
        response = session.get(registration_url)
    
    if confirmation_str in response.text:
        print(f"SIGNED UP {email}")
    else:
        print(f"NOT SIGNED UP {email}")
    


def monitor_full_event(email, registration_url, session):
    event_time_utc = parse(parse_qs(urlparse(registration_url).query)['spilletid'][0]).astimezone(pytz.UTC)

    response = session.get(registration_url)
    while confirmation_str not in response.text:
        print(f"{email} for {registration_url} monitoring waitlist")
        time_diff = time_diff_seconds(event_time_utc, parse(response.headers['Date']))
        if time_diff < 0:
            break
        time.sleep(30) #30 second sleep
        response = session.get(registration_url)

    if confirmation_str in response.text:
        print(f"SIGNED UP {email}")
    else:
        print(f"NOT SIGNED UP {email}")


# HELPER FUNCTIONS
def sanity_check_good(email, event_url):
    if not user_database.is_in_db(email):
        print(f"{email} not in database")
        return False
    if not is_valid_url(event_url):
        print(f"Invalid URL: {event_url}")
        return False
    return True


def log_in(user, session):
    homepage_url = "https://www.ntnuitennis.no/index.php?lang=no"
    login_values = {'email': user['email'],
                    'password': user['password'],
                    'lang': "no",
                    'rememberme': "on"}
    
    session.post(url=homepage_url, data=login_values)

def get_registration_url(event_url, vikar_id):
    return event_url + f'&leggtilvikarid={vikar_id}'

def is_valid_url(event_url):
    if "www.ntnuitennis.no" not in event_url:
        return False
    return True

def time_diff_seconds(time_a, time_b):
    return (time_a - time_b).total_seconds()