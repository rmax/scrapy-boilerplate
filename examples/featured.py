"""Stackoverflow's featured questions scraper.

Usage: scrapy runspider featured.py
"""
from scrapy_boilerplate import NewSpider, NewItem
from pyquery import PyQuery
from urlparse import urljoin


FeaturedItem = NewItem('title tags stats url')

MySpider = NewSpider('featured')


@MySpider.scrape('http://www.stackoverflow.com/?tab=featured')
def parse(spider, response):
    """Scrapes featured questions."""
    d = PyQuery(response.body)
    for summary in d('.question-summary'):
        el = d(summary)
        yield FeaturedItem(
            title=el.find('h3').text(),
            url=urljoin(response.url, el.find('h3 a').attr('href')),
            tags=[d(a).text() for a in el.find('.tags a')],
            stats={
                'votes': el.find('.votes .mini-counts').text(),
                'answers': el.find('.status .mini-counts').text(),
                'views': el.find('.views .mini-counts').text(),
            }
        )
    spider.log("Finished extracting featured questions")


if __name__ == '__main__':
    print __doc__
