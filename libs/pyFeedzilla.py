#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import urllib

class Categorie(object):
	def __init__(self, id, displayName, englishName, urlName):
		self.id = id
		self.displayName = displayName
		self.englishName = englishName
		self.urlName = urlName


class Article(object):
	def __init__(self, url, title, summary, publish_date, author, source):
		self.url = url
		self.title = title
		seld.summary = summary
		self.publish_date = publish_date
		self.author = author
		self.source = source


class APIFeedzilla(object):
	BASE_URL = 'http://api.feedzilla.com'

	