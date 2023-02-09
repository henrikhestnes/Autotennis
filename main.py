from flask import Flask, render_template, request
import os, threading
import database
import booking

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def frontpage():
    return render_template('index.html')

@app.route('/submit_user', methods=['POST'])
def submit_user():
    email = request.form.get('email')
    password = request.form.get('password')
    vikar_id = request.form.get('vikar_id')
    if database.is_in_db(email):
        database.update(email, password, vikar_id)
    else:
        database.add_entry(email, password, vikar_id)
    return render_template('index.html')

@app.route('/submit_event', methods=['POST'])
def submit_event():
    email = request.form.get('email')
    url = request.form.get('url')
    t = threading.Thread(target=booking.schedule_booking, args=(email, url))
    t.start()
    return render_template('index.html')

@app.route('/submit_waitlist', methods=['POST'])
def submit_waitlist():
    email = request.form.get('email')
    url = request.form.get('url')
    t = threading.Thread(target=booking.monitor_full_event, args=(email, url))
    t.start()
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
