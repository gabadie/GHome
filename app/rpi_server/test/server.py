from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor
from uuid import getnode as get_mac
from twisted.web import xmlrpc, server
from config_rpi_serv import RpiGlobalConfig
import pymplb
#from py8tracks import API8tracks

class RpiServer(xmlrpc.XMLRPC):

	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
		config=RpiGlobalConfig().from_json('./configRpi.json')
		self.config=config

	def xmlrpc_play_music(self,url):
		print "ok, music is playing"  + url
		mplayer=pymplb.MPlayer()	
		mplayer.loadfile(url)
		return "ok, music is playing"  + url


if __name__=='__main__':

	from twisted.internet import reactor
	rpiServer=RpiServer()
	#launch client call to add this raspi to the main server
	proxy = Proxy('http://'+rpiServer.config.mainServerRpi.ip + ':' + str(rpiServer.config.mainServerRpi.port))
	proxy.callRemote('raspi.add_raspi',str(rpiServer.config.rpiServer.ip),rpiServer.config.rpiServer.port,str(get_mac()))
	#launch server 
	reactor.listenTCP(rpiServer.config.rpiServer.port,server.Site(rpiServer))
	reactor.run()
