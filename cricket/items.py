# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Cricket(scrapy.Item):
    """
    ニュースのヘッドラインを表すItem。
    """

    linked_information = scrapy.Field()
    article_body = scrapy.Field()
    URL = scrapy.Field()
    nickname = scrapy.Field()
    description = scrapy.Field()
