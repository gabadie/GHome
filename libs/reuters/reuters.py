#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
sys.path.append('../../libs')

import requests
import feedparser
from config import GlobalConfig
import mongoengine

config = GlobalConfig()
mongoengine.connect(config.mongo_db)



class Article(object):
	def __init__(self, title, link, description, category, **kwargs):
		self.title = title
		self.link = link
		self.description = description
		self.category = category


class APIReuters(object):
	BASE_URL = "http://feeds.reuters.com"

	def _request(self, path):
		# Building the query url
		query_url = '{}/{}'.format(APIReuters.BASE_URL, path)


		response = requests.get(query_url)

		if not response.ok:
			raise requests.HTTPError("Error while consuming the API with query: {}".format(response.request.path_url))
		else:
			return response.content


	def articles(self, path):


		rss_articles = self._request(path)
		xml_articles = feedparser.parse(rss_articles)
		article_list = []

		for item in xml_articles['entries']:
			article = Article(item.title, item.link, item.description, item.category)
			article_list.append(article)

		return article_list

class Article_base(mongoengine.Document):
	title = mongoengine.fields.StringField(required=False)
	link = mongoengine.fields.StringField(required=False)
	description = mongoengine.fields.StringField(required=False)
	category = mongoengine.fields.StringField(required=True)

			

if __name__ == '__main__':

	# Initializing the API
    api = APIReuters()

    Article_base.drop_collection()

    for article in api.articles("reuters/topNews"):
        arti = Article_base(article.title, article.link, article.description, article.category)
        arti.save()
        print '       Article : "{}" added to the database'.format(arti.title.encode('utf-8'))