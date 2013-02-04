"""Script to illustrates the use of `run_crawler` helper.

Usage::

    python crawler.py -h

    python crawler.py -l

    python crawler.py spider_one

"""
from scrapy_boilerplate import (run_crawler, SpiderManager, NewItem,
                                NewSpider, NewCrawlSpider)
from scrapy.spider import BaseSpider


BaseItem = NewItem('spider url')

ItemOne = NewItem('title', base_cls=BaseItem)
ItemTwo = NewItem('name', base_cls=BaseItem)
ItemThree = NewItem('data', base_cls=BaseItem)


class SpiderOne(BaseSpider):
    name = 'spider_one'
    start_urls = ['http://example.org']

    def parse(self, response):
        return ItemOne(
            title='welcome to example.org',
            spider=self.name,
            url=response.url,
        )


SpiderTwo = NewSpider('spider_two')


@SpiderTwo.scrape('http://example.net')
def parse_net(spider, response):
    return ItemTwo(
        name='foo',
        spider=spider.name,
        url=response.url,
    )


SpiderThree = NewCrawlSpider('spider_three')


if __name__ == '__main__':
    # register spiders classes in the spider manager so
    # the crawler knows which ones are available
    SpiderManager.register(SpiderOne)
    SpiderManager.register(SpiderTwo)
    #SpiderManager.register(SpiderThree)

    run_crawler()
