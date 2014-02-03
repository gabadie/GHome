import sys
sys.path.append('..')
sys.path.append('../../libs')

from shopsense.shopstyle import ShopStyle
from config import GlobalConfig

config = GlobalConfig()

s = ShopStyle(config.api_shopstyle)

if __name__ == '__main__':
    # mens-clothes
    # 'women'
    print [c['id'] for c in s.categories()['categories'] if 'pants' in c['id'].lower()]


