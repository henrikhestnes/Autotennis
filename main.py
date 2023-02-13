from flask import Flask, render_template, request
import threading

import user_database
import booking_database
import fsm


app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def frontpage():
    return render_template('index.html', registered_emails=user_database.get_registered_emails())

@app.route('/submit_user', methods=['POST'])
def submit_user():
    email = request.form.get('email')
    password = request.form.get('password')
    vikar_id = request.form.get('vikar_id')
    print(f'ADDING {email} TO DATABASE')
    if user_database.is_in_db(email):
        user_database.update(email, password, vikar_id)
    else:
        user_database.add_entry(email, password, vikar_id)
    return render_template('index.html', registered_emails=user_database.get_registered_emails())

@app.route('/submit_event', methods=['POST'])
def submit_event():
    email = request.form.get('email')
    url = request.form.get('url')
    booking_database.add_entry(email, url)
    return render_template('index.html', registered_emails=user_database.get_registered_emails())

@app.route('/submit_waitlist', methods=['POST'])
def submit_waitlist():
    email = request.form.get('email')
    url = request.form.get('url')
    #TODO: Implement
    return render_template('index.html', registered_emails=user_database.get_registered_emails())


if __name__ == "__main__":
    t = threading.Thread(target=fsm.start)
    t.start()
    app.run(debug=True)
