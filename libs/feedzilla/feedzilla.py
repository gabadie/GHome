#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


class Categorie(object):
	def __init__(self, id, displayName, englishName, urlName):
		self.id = id
		self.displayName = displayName
		self.englishName = englishName
		self.urlName = urlName

class Article(object):
	def __init__(self, publish_date, source, source_url, summary, author, title, url, **kwargs):
		self.publish_date = publish_date
		self.source = source
		self.source_url = source_url
		self.summary = summary
		self.author = author
		self.title = title
		self.url = url

	def __str__(self):
		attrs = vars(self)
		return ', '.join("%s: %s" % item for item in attrs())
		# return 'date :' + self.publish_date + '\n' + 'source : ' +  self.source + '\n' + 'source_url : ' + self.source_url + '\n'+ 'resume : ' + self.summary + '\n'+ ' auteur : ' + self.author + '\n'+ 'titre : ' + self.title + '\n' + 'url :' + self.url

class APIFeedzilla(object):
	BASE_URL = 'http://api.feedzilla.com'

	def _request(self, path):
		# Building the query url
		query_url = '{}/{}.json'.format(APIFeedzilla.BASE_URL, path)


		response = requests.get(query_url)
		if not response.ok:
			raise requests.HTTPError("Error while consuming the API with query: {}".format(response.request.path_url))
		else:
			print response.json()
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

	def categorieById(self, category_id):

		categorie_list = self.categories()
		for category in categorie_list:
			if int(category.id) == int(category_id):
				return category
		print 'probleme'
		return 

	article_fields = ['publish_date', 'source', 'source_url', 'summary', 'author', 'title', 'url']
	def articles(self, category_id):

		path = '{}/{}/{}'.format('/v1/categories', category_id, 'articles')

		article_data_list = self._request(path)['articles']
		article_list = []


		for article_data in article_data_list:
			data = {field : article_data.get(field, '') for field in APIFeedzilla.article_fields}
			article = Article(**data)
			article_list.append(article)

		return article_list


if __name__ == '__main__':

	# Initializing the API
	api = APIFeedzilla()
	api.categories()
