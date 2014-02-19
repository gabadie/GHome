import sys
sys.path.append('..')
sys.path.append('../../libs')

from datetime import datetime

import mongoengine

from shopsense.shopstyle import ShopStyle
from config import GlobalConfig
from meteo import Weather, get_current_weather
config = GlobalConfig()

shopstyle = ShopStyle(config.api_shopsense)

top_categories = ['shirt', 'dress', 'jacket', 't-shirt', 'pullover']
bottom_categories = ['jeans', 'pants', 'trouser', 'skirt', 'shorts']
feet_categories = ['shoe', 'shoes', 'heels', 'sandal', 'mocassin']

class Product(mongoengine.Document):
    id = mongoengine.IntField(required=True, primary_key=True)
    name = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)

    description = mongoengine.StringField(required=True)
    price = mongoengine.IntField(required=True)
    price_label = mongoengine.StringField(required=True)
    main_image = mongoengine.StringField(required=True)

    retailer = mongoengine.DictField(required=True)
    brand = mongoengine.DictField()
    categories = mongoengine.ListField(mongoengine.DictField(required=True))

    top = mongoengine.BooleanField(default=False)
    bottom = mongoengine.BooleanField(default=False)
    feet = mongoengine.BooleanField(default=False)

    images = mongoengine.DictField(required=True)

    def clean(self):
        self.name = self.name.encode('utf-8')

    @staticmethod
    def from_data(data):
        data['url'] = data['pageUrl']
        data['images'] = data['image']['sizes']
        data['price_label'] = data['priceLabel']
        data['main_image'] = data['images']['Original']['url']

        product = Product(**data)
        return product

    @staticmethod
    def from_pid(pid):
        data = shopstyle.product(pid)
        data['id'] = pid
        return Product.from_data(data)

    @staticmethod
    def search(query):
        query_result = shopstyle.search(query)
        return [Product.from_data(data) for data in query_result['products']]

    # mens-clothes
    # 'women'

class OutfitChoice(mongoengine.Document):

    top = mongoengine.ReferenceField(Product, required=True)
    bottom = mongoengine.ReferenceField(Product, required=True)
    feet = mongoengine.ReferenceField(Product, required=True)

    weather = mongoengine.ReferenceField(Weather, default=get_current_weather)
    date = mongoengine.DateTimeField(required=True, default=datetime.now)
    weekday = mongoengine.IntField(required=True)

    def clean(self):
        self.weekday = self.date.weekday()


def fetch_fashion():
    Product.drop_collection()

    # Adding products
    for query in top_categories:
        for p in Product.search(query):
            p.top = True
            p = p.save()
            print 'Added "{}"'.format(p.name)

    for query in bottom_categories:
        for p in Product.search(query):
            p.bottom = True
            p = p.save()
            print 'Added "{}"'.format(p.name)

    for query in feet_categories:
        for p in Product.search(query):
            p.feet = True
            p = p.save()
            print 'Added "{}"'.format(p.name)


if __name__ == '__main__':
    mongoengine.connect(config.mongo_db)
    fetch_fashion()
