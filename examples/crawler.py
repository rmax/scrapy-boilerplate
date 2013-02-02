"""Script to illustrates the use of `run_crawler` helper.

Usage::

    python run_scraper.py -h

    python run_scraper.py -l

    python run_scraper.py spider_one

"""
from scrapy_boilerplate import run_crawler, SpiderManager, ItemFactory
from scrapy.spider import BaseSpider


ItemOne = ItemFactory('title url')
ItemTwo = ItemFactory('name url')
ItemThree = ItemFactory('data url')


class SpiderOne(BaseSpider):
    name = 'spider_one'
    start_urls = ['http://example.org']

    def parse(self, response):
        return ItemOne(
            title='welcome to example.org',
            url=response.url,
        )


class SpiderTwo(BaseSpider):
    name = 'spider_two'
    start_urls = ['http://example.net']

    def parse(self, response):
        return ItemTwo(
            name='foo',
            url=response.url,
        )


class SpiderThree(BaseSpider):
    name = 'spider_three'
    start_urls = ['http://example.com']

    def parse(self, response):
        return ItemThree(
            data=[1,2,3],
            url=response.url,
        )



if __name__ == '__main__':
    # register spiders classes in the spider manager so
    # the crawler knows which ones are available
    SpiderManager.register(SpiderOne)
    #SpiderManager.register(SpiderTwo)
    SpiderManager.register(SpiderThree)

    run_crawler()
