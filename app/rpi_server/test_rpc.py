from twisted.web.xmlrpc import Proxy,reactor

from twisted.web import xmlrpc, server


def return_value(mess):
	print mess
	reactor.stop()

proxy = Proxy('http://127.0.0.1:8001')
proxy.callRemote('raspi.find_music_url',0,"").addCallbacks(return_value)
reactor.run()