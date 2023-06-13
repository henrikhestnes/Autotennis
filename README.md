# AUTOTENNIS
Automatic tennis or padel session booking using a Flask application hosted on Google Cloud Platform (GCP).

## Description
At NTNUI Tennis, you can sign up for available tennis or padel sessions 72 hours in advance. However, I found it cumbersome to remember to book the sessions 72 hours in advance and figured out it would be interesting and instructive to automate this process. This led to the development of this service, sparing me and my friends from the hassle of having to sit ready to book the sessions.

## Website
The website hosted on GCP is depicted below.
![image info](./pictures/autotennis.png)

## Usage
1. The user first registers its credentials, which get stored in a TinyDB database on GCP Bucket Storage.

After this, different approaches exist.
##### Scheduling bookings
2. After registration, the user can sign up for sessions. This is done by copying the link of the session the user wants to sign up for and pasting it into the sign-up form. This spawns a thread that sends an HTTP post request is sent to the website, which logs the user in and determines how long time it is until registration.
3. If it is more than 72 hours until registration opens, the thread sleeps half the time difference before waking up and checking the time difference. This is repeated until the time difference is less than 5 seconds. The thread then starts sending HTTP post requests for signing up until the user is signed up.
4. If the recurring box is marked on sign-up, this procedure is repeated weekly by updating the HTTP request with the endpoint of the following session.
##### Waitlist
2. If the session is already fully booked, the user can add itself to a waitlist. The code then spawns a thread that tries to sign the user up every 30 seconds until the user is signed up or the event has passed.

## Disclaimer
I am no expert in network programming, and this is, in fact, the first time I have done it in Python. The implemented network code probably bears the mark of this🤠
