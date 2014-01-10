import sys
sys.path.insert(0, '..')

from flask import Flask, render_template, request

from model import device




app = Flask(__name__)

@app.route('/')
def index():
	devices = [device.Device('1337', None), device.Device('4242', None)]
	return render_template('index.html', devices=devices)

@app.route('/hello')
def hello():
    return 'Hello World'

if __name__ == "__main__":
    app.run(debug=True, port=5000)