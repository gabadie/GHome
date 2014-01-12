#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../libs')

from geopy import geocoders
from shopsense.shopstyle import ShopStyle
from metwit import Metwit
SHOPSENSE_ID = 'uid3444-24262962-52'

# Testing geolocation
g = geocoders.GoogleV3()
address = raw_input("Where do you live? ")
localization = g.geocode(address)
if localization:
	place, (lat, lng) = localization
	print "Your location = {} | (lat:{}, lng:{})".format(place, lat, lng)
else:
	print "Location unkown"
	lat, lng = 42, 42

# Testing Metwit weather
print ""
print "Weather:"
weather = Metwit.weather.get(location_lat=lat, location_lng=lng)
weather_now = weather[0]['weather']
status = weather_now['status']
temperature, humidity = weather_now['measured']['temperature'], weather_now['measured']['humidity']
print "Status: {}, Temperature: {}°F, Humidity: {}".format(status, temperature, humidity)
print ''

# Testing shopsense
s = ShopStyle(SHOPSENSE_ID)
clothes_search = raw_input("What type of clothes are you looking for? ")
products = s.search(clothes_search)['products']

print ""
for product in products:
	name = product['name']
	price = product['salePriceLabel'] if 'salePriceLabel' in product else 'Unknown'
	name = name.encode('utf-8')

	print "{} : {}".format(name, price)
	print "-" * 80