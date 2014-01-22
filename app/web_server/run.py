from flask import Flask, render_template, request
import json
import sys
sys.path.insert(0, '..')
sys.path.insert(0, '../../libs/py8tracks')

from py8tracks import API8tracks
from config import GlobalConfig
config = GlobalConfig()

from twisted.web.xmlrpc import Proxy,reactor

from twisted.web import xmlrpc, server


app = Flask(__name__)




@app.route('/player', methods=['POST','GET'])
def playMusic():
    if request.method == 'POST':
        form=request.form
        tag =  [form.get(val) for val in ['tag']]
        print tag

        api=API8tracks(config.api_8tracks)

        mixset = api.mixset(tags=tag, sort='popular')
        print mixset
        url= "http://streamTaMaman.wav" # [stream.data['track_file_stream_url'] for stream in mixset.mixes[0].tracks_cache]
        proxy = Proxy('http://'+str(config.main_server.ip)+':'+str(config.main_server.rpc_port))
        proxy.callRemote('raspi.find_music_url',0,url).addCallbacks(return_value)
        reactor.run()
        # TODO : this is blocking, warning!!
    return json.dumps("haha")

def return_value(mess):
    print mess
    reactor.stop()

@app.route('/')
def index():
    user="Adrien"
    combo_options = ["jazzy", "happy", "sad", "worry"]
    return render_template("music.html", combo_options = combo_options,user=user )


if __name__=="__main__" :
    app.run(debug = True)