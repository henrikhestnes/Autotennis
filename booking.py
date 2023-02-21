import requests
import threading
import time, pytz
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from dateutil.parser import parse

import user_database
import booking_database
import custom_logging

confirmation_str = "Kode for tilgang til bygget:"

def boot():
    for booking in booking_database.get_all_entries():
        email = booking['email']
        event_url = booking['event_url']
        t = threading.Thread(target=book, args=(email, event_url))
        t.start()
        custom_logging.info(f"RESTARTING THREAD {email} FOR {booking}")

def book(email, event_url):
    if not sanity_check_good(email, event_url):
        booking_database.remove_entry(email, event_url)
        custom_logging.info(f"INVALID URL: {event_url}")
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
    custom_logging.info(f"{email} FOR {event_time} EXITING")


def schedule_booking(email, event_url, registration_url, utc_registration_time, session):
    response = session.get(event_url)
    registration_time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
    
    while registration_time_diff > 5:
        response = session.get(event_url)
        registration_time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
        custom_logging.info(f"{email} for {utc_registration_time + timedelta(hours=72)} sleeping {registration_time_diff/2} seconds")
        time.sleep(registration_time_diff/2)

    response = session.get(registration_url)
    i = 0
    while registration_time_diff > -10:
        if i % 10 == 0:
            registration_time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
        response = session.get(registration_url)
        i += 1
    
    if confirmation_str in response.text:
        custom_logging.info(f"SIGNED UP {email} at {parse(response.headers['Date'])}, {i} attempts")
    else:
        custom_logging.info(f"NOT SIGNED UP {email}, {i} attempts")
    


def monitor_full_event(email, registration_url, session):
    event_time_utc = parse(parse_qs(urlparse(registration_url).query)['spilletid'][0]).astimezone(pytz.UTC)

    response = session.get(registration_url)
    i = 0
    while confirmation_str not in response.text:
        if i % 20 == 0: #Every 10 minute
            custom_logging.info(f"{email} for {registration_url} monitoring waitlist")
            i = 0
        i += 1

        time_diff = time_diff_seconds(event_time_utc, parse(response.headers['Date']))
        if time_diff < 0:
            break
        time.sleep(30) #30 second sleep
        response = session.get(registration_url)

    if confirmation_str in response.text:
        custom_logging.info(f"SIGNED UP {email} at {parse(response.headers['Date'])}")
    else:
        custom_logging.info(f"NOT SIGNED UP {email}")


# HELPER FUNCTIONS
def sanity_check_good(email, event_url):
    if not user_database.is_in_db(email):
        custom_logging.info(f"{email} not in database")
        return False
    if not is_valid_url(event_url):
        custom_logging.info(f"Invalid URL: {event_url}")
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

def time_diff_seconds(time_a, time_b):
    return (time_a - time_b).total_seconds()