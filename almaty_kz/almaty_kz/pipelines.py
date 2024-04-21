# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

class AlmatyKzPipeline:
    def is_digit(self, _str):
        if _str is None:
            return None
        if isinstance(_str, int):
            return _str
        flag = all(ch.isdigit() for ch in _str)
        return int(_str) if flag else None
    
    def process_item(self, item, spider):
        item['row'] = self.is_digit(item['row'])
        item['seat'] = self.is_digit(item['seat'])
        item['price'] = self.is_digit(item['price'])
        item['count'] = self.is_digit(item['count'])
        return item
