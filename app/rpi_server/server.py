from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor
from uuid import getnode as get_mac
from twisted.web import xmlrpc, server
from config_rpi_serv import RpiGlobalConfig
import pymplb
import socket
import json

#from py8tracks import API8tracks

DEFAULT_IP = "10.0.0.42"


class MusicPlayer(object):

    def __init__(self):
        self.mplayer=pymplb.MPlayer()
        self.musics=[] # [{'name':     ,'stream_url':    , 'img_url':      }, { ...... }]
        self.current_music=0
        self.is_pausing=False
        self.tags=[]

    def next(self):
        if self.current_music+1 < len(self.musics):
            print "next music"
            self.current_music+=1
            self.mplayer.stop()
            self.mplayer.loadfile(str(self.musics[self.current_music]['stream_url']))
            return True
        else:
            print "end reach"
            return False

    def previous(self):
        if self.current_music-1 >=0 and self.current_music-1<len(self.musics) :
            print "previous music"
            self.current_music-=1
            self.mplayer.stop()
            self.mplayer.loadfile(str(self.musics[self.current_music]['stream_url']))
            return True
        else :
            print "end reach"
            return False

class RpiServer(xmlrpc.XMLRPC):

    def __init__(self):
        xmlrpc.XMLRPC.__init__(self)
        config=RpiGlobalConfig().from_json('./configRpi.json')
        self.config=config
        self.ip=self.getAddress()
        self.port=config.rpiServer.port
        self.macAddress=str(get_mac())
        self.music_player=MusicPlayer()

    def xmlrpc_init_play_music(self,urls,tags):
        urls_splitted=json.loads(urls)
        print "ok, music is playing"  #+ str(urls_splitted[0])
        self.music_player.musics=urls_splitted
        self.music_player.tags.append(tags)
        print urls_splitted
        print urls
        if len(urls_splitted)>0:
            self.music_player.mplayer.loadfile(str(urls_splitted[0]['stream_url']))
        return str(urls_splitted[0]['name'])

    def xmlrpc_next_music(self):
        self.music_player.next()
        return str(self.music_player.musics[self.music_player.current_music]['name'])

    def xmlrpc_previous_music(self):
        self.music_player.previous()
        return str(self.music_player.musics[self.music_player.current_music]['name'])

    def xmlrpc_stop_music(self):
        print "stop music"
        self.music_player.mplayer.stop()
        return True

    def xmlrpc_pause_music(self):

        if self.music_player.is_pausing == True:
            self.music_player.is_pausing=False
            self.music_player.mplayer.pause()
            print "playing"
            return False
        else :
            self.music_player.is_pausing=True
            self.music_player.mplayer.pause()
            print "pausing"
            return True

    def xmlrpc_play_music(self,stream = ""):
        if self.music_player.is_pausing == True:
            self.music_player.mplayer.pause()
            self.music_player.is_pausing = False
            return True
        elif not stream == "" :
            self.music_player.musics = stream
            self.music_player.current_music = 0
            self.music_player.mplayer.loadfile(stream)
            return True
        else :
            return False

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

    rpiServer=RpiServer()
    #launch client call to add this raspi to the main server
    proxy = Proxy('http://'+rpiServer.config.mainServerRpi.ip + ':' + str(rpiServer.config.mainServerRpi.port))
    proxy.callRemote('raspi.add_raspi',rpiServer.ip,rpiServer.port,rpiServer.macAddress)
    #launch server
    reactor.listenTCP(rpiServer.config.rpiServer.port,server.Site(rpiServer))
    reactor.run()
