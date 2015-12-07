# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class MedItem(Item):
    #post info
    post_url = Field()
    post_id = Field()
    title = Field()
    reply_num = Field()

    #poster info
    poster_id = Field()
    #poster_demo = Field()
    #poster_interest = Field()

    #post
    question = Field()
    replies = Field()





    
