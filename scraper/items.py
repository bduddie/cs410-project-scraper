# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ForumThread(scrapy.Item):
    topic = scrapy.Item()
    op = scrapy.Item()

class ForumPost(scrapy.Item):
    author = scrapy.Item()
    content = scrapy.Item()
