# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OhioenergyItem(scrapy.Item):
    # define the fields for your item here like:
    table_id = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field()
    rate_type = scrapy.Field()
    percent_renewable = scrapy.Field()
    intro_price = scrapy.Field()
    term_length = scrapy.Field()
    early_term_fee = scrapy.Field()
    promo_offer = scrapy.Field()
    # pass
