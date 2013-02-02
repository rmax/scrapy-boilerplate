"""Stackoverflow's featured questions scraper.

Usage: scrapy runspider featured.py
"""
from scrapy_boilerplate import spider_factory, ItemFactory
from pyquery import PyQuery
from urlparse import urljoin


FeaturedItem = ItemFactory('title tags stats url')


@spider_factory('http://www.stackoverflow.com/?tab=featured')
def FeaturedSpider(response):
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


if __name__ == '__main__':
    print __doc__
