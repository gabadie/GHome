from py8tracks import py8tracks
from pymplb import pymplb
from time import sleep
import json

import sys
sys.path.insert('../libs')

tags_input = raw_input("What type of music do you like? (tags separated by a comma) ")
tags = tags_input.split(',')

# Loading the API key from a configuration file
with open('config.json') as config_file:
	config = json.loads(config_file.read())
	api_key = config['8tracks_api_key']

# Initializing the API
api = py8tracks.API8tracks(api_key)

# Intializing mplayer
mplayer = pymplb.MPlayer()

# Search mixes based on multiple criterias
mixset = api.mixset(tags=tags, sort='popular') 
print mixset
for mix in mixset.mixes:
	print ""
	print mix
	for song in mix:
		print song
		print '-' * 80
		mplayer.loadfile(str(song.data['track_file_stream_url']))
		sleep(10)
