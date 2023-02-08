from flask import Flask, render_template, request

app = Flask(__name__)
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/', methods=['POST', 'GET'])
def form():
    return render_template('index.html')

@app.route('/submit_user', methods=['POST'])
def submit_user():
    email = request.form.get('email')
    password = request.form.get('password')
    vikar_id = request.form.get('vikar_id')
    return f'{email} {password} {vikar_id}'

@app.route('/submit_event', methods=['POST'])
def submit_event():
    email = request.form.get('email')
    url = request.form.get('url')
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
