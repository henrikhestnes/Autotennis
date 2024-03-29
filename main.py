from flask import Flask, render_template, request, redirect
import threading

import user_database
import booking_database
import booking
import custom_logging


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def frontpage():
    return render_template('index.html', active_bookings=booking_database.get_active_bookings_per_user())


@app.route('/submit_user', methods=['POST'])
def submit_user():
    email = request.form.get('email')
    password = request.form.get('password')
    vikar_id = request.form.get('vikar_id')
    custom_logging.info(f'ADDING {email} TO DATABASE')
    if user_database.is_in_db(email):
        user_database.update(email, password, vikar_id)
    else:
        user_database.add_entry(email, password, vikar_id)
    return redirect('/')


@app.route('/submit_event', methods=['POST'])
def submit_event():
    email = request.form.get('email')
    url = request.form.get('url')
    recurring = bool(request.form.get('recurring'))
    if not booking_database.is_in_db(email, url):
        booking_database.add_entry(email, url, recurring, "schedule")
        t = threading.Thread(target=booking.book, args=(email, url))
        t.start()
    else:
        custom_logging.info(f'{email} for {url} ALREADY EXISTS')
    return redirect('/')

@app.route('/remove_recurring', methods=['POST'])
def remove_recurring():
    email = request.form.get('email')
    url = request.form.get('url')
    if booking_database.is_in_db(email, url):
        booking_database.remove_entry(email, url)
    return redirect('/')

@app.route('/submit_waitlist', methods=['POST'])
def submit_waitlist():
    email = request.form.get('email')
    url = request.form.get('url')
    if not booking_database.is_in_db(email, url):
        booking_database.add_entry(email, url, False, "monitor")
        t = threading.Thread(target=booking.book, args=(email, url))
        t.start()
    return redirect('/')

custom_logging.info("BOOTING")
user_database.sync()
booking_database.sync()
booking.boot()

if __name__ == "__main__":
    app.run()
