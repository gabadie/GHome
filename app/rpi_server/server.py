from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor
from uuid import getnode as get_mac
from twisted.web import xmlrpc, server
from config_rpi_serv import RpiGlobalConfig
import pymplb
import socket
 
#from py8tracks import API8tracks

DEFAULT_IP = "10.0.0.42"

class RpiServer(xmlrpc.XMLRPC):

	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
		config=RpiGlobalConfig().from_json('./configRpi.json')
		self.config=config
		self.ip=self.getAddress()
		self.port=config.rpiServer.port
		self.macAddress=str(get_mac())

	def xmlrpc_play_music(self,url):
		print "ok, music is playing"  + str(url)
		mplayer=pymplb.MPlayer()	
		mplayer.loadfile(url)
		return "ok, music is playing "  + str(url)

	def getAddress(self):
	    try:
	        address = socket.gethostbyname(socket.gethostname())
	        # This often give 127.0.0.1, so ...
	    except:
	        address = ''
	    if not address or address.startswith('127.'):
	        # ...the hard way.
	        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	        s.connect((DEFAULT_IP, 0))
	        address = s.getsockname()[0]
	    return address


if __name__=='__main__':

	from twisted.internet import reactor
	rpiServer=RpiServer()
	#launch client call to add this raspi to the main server
	proxy = Proxy('http://'+rpiServer.config.mainServerRpi.ip + ':' + str(rpiServer.config.mainServerRpi.port))
	proxy.callRemote('raspi.add_raspi',rpiServer.ip,rpiServer.port,rpiServer.macAddress)
	#launch server 
	reactor.listenTCP(rpiServer.config.rpiServer.port,server.Site(rpiServer))
	reactor.run()
