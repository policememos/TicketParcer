# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class AlmatyKzItem(Item):
    sector = Field()
    row = Field()
    seat = Field()
    price = Field()
    count = Field()
