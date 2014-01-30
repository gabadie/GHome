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
	def __init__(self, publish_date, source, source_url, summary, author, title, url):
		self.publish_date = publish_date
		self.source = source
		self.source_url = source_url
		self.summary = summary
		self.author = author
		self.title = title
		self.url = url

class APIFeedzilla(object):
	BASE_URL = 'http://api.feedzilla.com'

	def _request(self, path):
		# Building the query url
		query_url = '{}/{}.json'.format(APIFeedzilla.BASE_URL, path)


		response = requests.get(query_url)
		if not response.ok:
			raise requests.HTTPError("Error while consuming the API with query: {}".format(response.request.path_url))
		else:
			return response.json()

	def categories(self):

		path = '{}'.format('/v1/categories')

		categorie_list = []
		categories_data_list = self._request(path)

		for categorie_data in categories_data_list:
			categorie = Categorie(categorie_data['category_id'], 
				categorie_data['display_category_name'], categorie_data['english_category_name'], 
				categorie_data['url_category_name'])
			categorie_list.append(categorie)

		return categorie_list

	def articles(self, category_id):

		path = '{}/{}/{}'.format('/v1/categories', category_id, 'articles')

		article_data_list = self._request(path)['articles']
		article_list = []

		for article_data in article_data_list:
			if 'publish_date' in article_data:
				pub = article_data['publish_date']
			else: 
				pub = ''
			if 'source' in article_data:
				sou = article_data['source']
			else:
				sou = ''
			if 'source_url' in article_data:
				souUrl = article_data['source_url']
			else:
				souUrl = ''
			if 'summary' in article_data:
				summ = article_data['summary']
			else:
				summ = ''
			if 'author' in article_data:
				aut = article_data['author']
			else:
				aut = ''
			if 'title' in article_data:
				tit = article_data['title']
			else:
				tit = ''
			if 'url' in article_data:
				url = article_data['url'] 
			else:
				url = ''
			article = Article(pub, sou, souUrl, summ, aut, tit, url)
			article_list.append(article)

		return article_list


if __name__ == '__main__':

	# Initializing the API
	api = APIFeedzilla()

	#cat = api.categories()
	#for caty in cat:
	#	print(caty.englishName)

	#articles = api.articles(13)
	#for art in articles:
	#	print art.source_url
