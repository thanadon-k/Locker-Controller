from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/controller', methods=['GET', 'POST'])
def controller():
    return render_template('controller.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
