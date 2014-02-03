import sys
sys.path.append('..')
sys.path.append('../../libs')

from shopsense.shopstyle import ShopStyle
from config import GlobalConfig
import mongoengine

config = GlobalConfig()
mongoengine.connect(config.mongo_db)
shopstyle = ShopStyle(config.api_shopstyle)


class Product(mongoengine.Document):
    id = mongoengine.fields.IntField(required=True, primary_key=True)
    name = mongoengine.fields.StringField(required=True)
    url = mongoengine.fields.StringField(required=True)

    description = mongoengine.fields.StringField(required=True)
    price = mongoengine.fields.IntField(required=True)
    price_label = mongoengine.fields.StringField(required=True)


    retailer = mongoengine.fields.DictField(required=True)
    brand = mongoengine.fields.DictField(required=True)
    categories = mongoengine.fields.ListField(mongoengine.fields.DictField(required=True))

    images = mongoengine.fields.ListField(mongoengine.fields.DictField(required=True))

    @staticmethod
    def from_data(data):
        data['url'] = data['pageUrl']
        data['images'] = [c['image']['sizes'] for c in data['colors']]
        data['price_label'] = data['priceLabel']
        product = Product(**data)
        return product

    @staticmethod
    def from_pid(pid):
        data = shopstyle.product(pid)
        data['id'] = pid
        return Product.from_data(data)

if __name__ == '__main__':
    # mens-clothes
    # 'women'
    print Product.from_pid(429844438).save().to_json()
