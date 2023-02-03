# URL of event you want to sign up to
event_url = 'https://www.ntnuitennis.no/timeinfo.php?timeid=233&spilletid=20230205T15:00:00&lang=no'



# Getting credentials
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='./abhi_credentials.env')
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




# Try to reserve spot
import time
confirmation_str = "Kode for tilgang til bygget:"
response = s.get(registration_url)
while confirmation_str not in response.text:
    print(f'Time: {time.ctime(time.time())}')
    time.sleep(30) #30 second sleep
    response = s.get(registration_url)





#Check if working
if confirmation_str in response.text:
    print("Woop woop time to kick ass")
else:
    print("Buhu dunno why but it didn't work:(")
