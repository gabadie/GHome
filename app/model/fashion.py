import sys
sys.path.append('..')
sys.path.append('../../libs')

from shopsense.shopstyle import ShopStyle
from config import GlobalConfig
import mongoengine

config = GlobalConfig()
mongoengine.connect(config.mongo_db)
shopstyle = ShopStyle(config.api_shopsense)


class Product(mongoengine.Document):
    id = mongoengine.fields.IntField(required=True, primary_key=True)
    name = mongoengine.fields.StringField(required=True)
    url = mongoengine.fields.StringField(required=True)

    description = mongoengine.fields.StringField(required=True)
    price = mongoengine.fields.IntField(required=True)
    price_label = mongoengine.fields.StringField(required=True)
    main_image = mongoengine.fields.StringField(required=True)

    retailer = mongoengine.fields.DictField(required=True)
    brand = mongoengine.fields.DictField()
    categories = mongoengine.fields.ListField(mongoengine.fields.DictField(required=True))

    images = mongoengine.fields.DictField(required=True)

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

if __name__ == '__main__':
    # mens-clothes
    # 'women'

    Product.drop_collection()

    for query in ['jean', 'skirt', 'shirt', 'pants', 'dress', 'hat', 'belt', 'jacket', 'pullover', 'hoodie', 'sweater']:
        for p in Product.search(query):
            p.save()
            print '"{}" added to the database'.format(p.name.encode('utf-8'))

    # Product(429844438).delete()
    # Product.from_pid(429844438).save().to_json()
