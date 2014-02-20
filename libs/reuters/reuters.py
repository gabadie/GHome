#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
sys.path.append('../../app')

import requests
import feedparser
import re
from goose import Goose
from config import GlobalConfig
import mongoengine



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


	def articles(self, path, g):

		
		rss_articles = self._request(path)
		xml_articles = feedparser.parse(rss_articles)
		article_list = []

		for item in xml_articles['entries']:
			title = ''
			link = ''
			description = ''
			category = ''
			if hasattr(item, 'title'):
				title = item.title
			if hasattr(item, 'link'):
				link = item.link
			if hasattr(item, 'description'):
				description = item.description
			if hasattr(item, 'category'):
				category_print = item.category[0].capitalize() + item.category[1:]
				category_list_print = re.findall('[A-Z][^A-Z]*', category_print)
				if (category_list_print[0] == 'Vc') or (category_list_print[0] == 'Wt'):
					category_list_print.pop(0)
				category = " ".join(category_list_print)
			
			article_goose = g.extract(url = link)
			if hasattr(article_goose.top_image, 'src'):
				image = article_goose.top_image.src
			else:
				image = None
			summary = article_goose.cleaned_text[:900]
			article = Article(title = title, link = link, description = description, category = category, summary = summary, image = image)
			article_list.append(article)

		return article_list


category_list = ["Top News", "Most Read", "Sports News", "World News", "Arts News", "Business News", "Media", "People News", "Business Travel", "Entertainment News", "Environment News", "Health News", "Company News", "Lifestyle Molt", "Oddly Enough News", "Politics News", "Science News", "Technology News", "Personal Finance", "Domestic News"]

class Article(mongoengine.Document):
	title = mongoengine.fields.StringField(required=False)
	link = mongoengine.fields.StringField(required=False)
	description = mongoengine.fields.StringField(required=False)
	category = mongoengine.fields.StringField(required=True)
	summary = mongoengine.fields.StringField(required=True)
	image = mongoengine.fields.StringField(required=False)

			

if __name__ == '__main__':
    config = GlobalConfig()
    mongoengine.connect(config.mongo_db)

	# Initializing the API
    api = APIReuters()
    g = Goose()
  #  Article.drop_collection()

    categories = ["reuters/topNews", "news/artsculture", "reuters/businessNews", "ReutersBusinessTravel", "reuters/companyNews", "reuters/entertainment", "reuters/environment", "reuters/healthNews", "reuters/lifestyle", "news/reutersmedia", "news/wealth", "reuters/MostRead", "reuters/oddlyEnoughNews", "reuters/peopleNews", "Reuters/PoliticsNews", "reuters/scienceNews", "reuters/sportsNews", "reuters/technologyNews", "Reuters/domesticNews", "Reuters/worldNews"]

    for category in categories:
    	print category
        for article in api.articles(category, g): 
        	article.save()
        	print '       Article : "{}" added to the database'.format(article.title.encode('utf-8'))