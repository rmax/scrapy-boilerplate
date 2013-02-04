"""Stackoverflow's top questions scraper.

Usage: scrapy runspider top.py

"""
from scrapy_boilerplate import NewCrawlSpider, NewItem
from pyquery import PyQuery
from urlparse import urljoin
from scrapy.http import Request


FeaturedItem = NewItem('title body tags user url')

TopSpider = NewCrawlSpider('top', start_urls=[
    'http://stackoverflow.com/?tab=hot',
])


@TopSpider.rule(r'/questions/\d+/[\w\-]+$')
def parse_question(spider, response):
    d = PyQuery(response.body)
    item = FeaturedItem(
        title=d('h1:first').text(),
        tags=[d(a).text() for a in d('.post-taglist a')],
        url=response.url,
    )
    # user page
    user_link = d('.post-signature .user-details a').attr('href')
    callback = spider.func_callback(parse_user, item=item)

    return Request(urljoin(response.url, user_link), callback=callback)


def parse_user(spider, response, item):
    # extract user info
    d = PyQuery(response.body)
    item['user'] = {
        'name': d('#user-displayname').text(),
        'about': d('#large-user-info .user-about-me').text(),
        'location': d('#large-user-info .adr').text(),
        'website': d('#large-user-info .url').attr('href'),
        'url': response.url,
    }
    yield item


if __name__ == '__main__':
    print __doc__
