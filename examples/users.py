"""Stackoverflow's users scraper.

Usage: scrapy runspider users.py
"""
from scrapy_boilerplate import NewCrawlSpider, NewItem
from pyquery import PyQuery


UserItem = NewItem('name about location website url')

UsersSpider = NewCrawlSpider('users', start_urls=[
    'http://stackoverflow.com/users?tab=reputation&filter=week',
])

UsersSpider.follow(r'/users\?page=\d+')


@UsersSpider.rule(r'/users/\d+/\w+')
def parse_tags(spider, response):
    d = PyQuery(response.body)
    yield UserItem(
        name=d('#user-displayname').text(),
        about=d('#large-user-info .user-about-me').text(),
        location=d('#large-user-info .adr').text(),
        website=d('#large-user-info .url').attr('href'),
        url=response.url,
    )


if __name__ == '__main__':
    print __doc__
