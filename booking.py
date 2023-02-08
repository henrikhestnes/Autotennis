import requests
import time, pytz
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from dateutil.parser import parse
import database

confirmation_str = "Kode for tilgang til bygget:"


def schedule_booking(email, event_url):
    s = requests.Session()

    if not is_valid_url(event_url, s):
        return
    
    user = database.get_entry(email)
    log_in(user, s)

    # Signing up
    registration_url = get_registration_url(event_url, user['vikar_id'])

    event_time = parse(parse_qs(urlparse(event_url).query)['spilletid'][0])
    registration_time = event_time - timedelta(hours=72)
    utc_registration_time = registration_time.astimezone(pytz.UTC)


    print("BOOKING")
    response = s.get(event_url)
    time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
    while time_diff > 3:
        response = s.get(event_url)
        time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
        time.sleep(time_diff/2)

    response = s.get(registration_url)
    while confirmation_str not in response.text:
        time_diff = time_diff_seconds(utc_registration_time, parse(response.headers['Date']))
        if time_diff < -60:
            break
        time.sleep(0.05) #0.05 second sleep to avoid ddos
        response = s.get(registration_url)


def monitor_full_event(email, event_url):
    s = requests.Session()

    if not is_valid_url(event_url, s):
        return

    user = database.get_entry(email)
    log_in(user, s)

    registration_url = get_registration_url(event_url, user['vikar_id'])

    # Try to reserve spot
    event_time_utc = parse(parse_qs(urlparse(event_url).query)['spilletid'][0]).astimezone(pytz.UTC)

    response = s.get(registration_url)
    while confirmation_str not in response.text:
        time_diff = time_diff_seconds(event_time_utc, parse(response.headers['Date']))
        if time_diff < 0:
            return
        time.sleep(30) #30 second sleep
        response = s.get(registration_url)



# HELPER FUNCTIONS
def log_in(user, session):
    homepage_url = "https://www.ntnuitennis.no/index.php?lang=no"
    login_values = {'email': user['email'],
                    'password': user['password'],
                    'lang': "no",
                    'rememberme': "on"}
    
    session.post(url=homepage_url, data=login_values)

def get_registration_url(event_url, vikar_id):
    return event_url + f'&leggtilvikarid={vikar_id}'

def is_valid_url(event_url, session):
    r = session.get(event_url)
    if 'ERROR' in r.text:
        return False
    return True

def time_diff_seconds(time_a, time_b):
    return (time_a - time_b).total_seconds()