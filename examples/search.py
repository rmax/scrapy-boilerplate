"""Displays Stackoverflow's search results for given query.

Usage: python search.py <query>
"""
import sys
from scrapy_boilerplate import NewSpider, run_spider
from pyquery import PyQuery
from urlparse import urljoin


SearchSpider = NewSpider('search')


if __name__ == '__main__':
    if not sys.argv[1:]:
        print __doc__
        sys.exit(2)

    query = ' '.join(sys.argv[1:])
    url = 'http://stackoverflow.com/search?q=%s' % query
    results = []

    # register scrape function dynamically to perform the query
    @SearchSpider.scrape(url)
    def parse(spider, response):
        d = PyQuery(response.body)
        results.extend(
            (d(e).text(), urljoin(response.url, d(e).attr('href')))
            for e in d('.result-link a')
        )

    # run spider to collect results
    run_spider(SearchSpider(), {
        'LOG_ENABLED': False,  # shut up log
    })

    # output results
    for i, (title, url) in enumerate(results, 1):
        print '%2d. %s\n    %s\n' % (i, title, url)
