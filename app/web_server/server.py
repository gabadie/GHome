import sys
sys.path.insert(0, '..')

from flask import Flask, render_template, request
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.internet import reactor

from model import device

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
	devices = [device.Device('1337'), device.Device('4242')]
	return render_template('index.html', devices=devices)

@app.route('/hello')
def hello():
    return 'Hello World'

if __name__ == "__main__":
	#app.run(5000, debug=True)

	resource = WSGIResource(reactor, reactor.getThreadPool(), app)
	site = Site(resource)

	reactor.listenTCP(5000, site)
	reactor.run()
