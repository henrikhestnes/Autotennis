# URL of event you want to sign up to
event_url = 'https://www.ntnuitennis.no/timeinfo.php?timeid=65&spilletid=20230207T15:00:00&lang=no'





# Getting credentials
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='./credentials.env')
#YOU NEED TO CHANGE THESE PARAMETERS IF YOU DO NOT STORE THEM IN A CREDENTIALS.ENV FILE
email = os.getenv('email')
password = os.getenv('password')
vikar_id = os.getenv('vikar_id')

registration_url = event_url + f'&leggtilvikarid={vikar_id}'





# Logging in
import requests

s = requests.Session()

home_url = "https://www.ntnuitennis.no/index.php?lang=no"
login_values = {'email': email,
                'password': password,
                'lang': "no",
                'rememberme': "on"}
r = s.post(url=home_url, data=login_values)





# Signing up
from urllib.parse import urlparse, parse_qs
from dateutil.parser import parse
from datetime import timedelta
import time
import pytz

event_time = parse(parse_qs(urlparse(event_url).query)['spilletid'][0])
registration_time = event_time - timedelta(hours=72)
utc_registration_time = registration_time.astimezone(pytz.UTC)

time_diff = float('inf')
while time_diff > 3: #to not kill the server too early
    response = s.get(event_url)
    time_diff = (utc_registration_time - parse(response.headers['Date'])).total_seconds()
    print(f"Time to registration: {time_diff} seconds")
    time.sleep(1) #second

confirmation_str = "Kode for tilgang til bygget:"
response = s.get(registration_url)
while confirmation_str not in response.text:
    time_diff = (utc_registration_time - parse(response.headers['Date'])).total_seconds()
    if time_diff < -60:
        print("Time since registration exceeds 60 sec")
        break
    time.sleep(0.05) #0.05 second sleep to avoid ddos
    response = s.get(registration_url)





#Check if working
if confirmation_str in response.text:
    print("Woop woop time to kick ass")
else:
    print("Buhu dunno why but it didn't work:(")
