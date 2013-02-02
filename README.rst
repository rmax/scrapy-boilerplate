==================
scrapy-boilerplate
==================

`scrapy-boilerplate` is a small set of utilities for `Scrapy`_ to simplify
writing low-complexity spiders that are very common in small and one-off projects.

It requires `Scrapy`_ `(>= 0.16)` and has been tested using `python 2.7`.
Additionally, `PyQuery`_ is required to run the scripts in the `examples`_
directory.

.. note:: The code is highly experimental and should be used with caution.


-----------
Usage Guide
-----------

Items
=====

Standard item definition::

  from scrapy.item import Item, Field

  class MyItem(Item):
      title = Field()
      body = Field()
      price = Field()
      url = Field()


Becomes::

  from scrapy_boilerplate import ItemFactory

  MyItem = ItemFactory('title body price url')


BaseSpider
==========

Standard spider definition::

  from scrapy.spider import BaseSpider

  class MySpider(BaseSpider):
      name = 'my_spider'
      start_urls = ['http://example.com']

      def parse(self, response):
          # do stuff


Becomes::

  from scrapy_boilerplate import spider_factory

  @spider_factory('http://example.com')
  def MySpider(response):
      # do stuff


CrawlSpider
===========

Standard spider definition::

  from scrapy.contrib.spiders import CrawlSpider, Rule
  from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor


  class MySpider(CrawlSpider):
      name = 'example.com'
      start_urls = ['http://example.com']

      rules = (
          Rule(SgmlLinkExtractor('category\.php'), follow=True),
          Rule(SgmlLinkExtractor('item\.php'), callback='parse_item'),
      )

      def parse_item(self, response):
          # do stuff


Becomes::

  from scrapy_boilerplate import NewCrawlSpider

  MySpider = NewCrawlSpider('example.com')
  MySpider.follow('category\.php')

  @MySpider.rule('item\.php')
  def parse_item(response):
      # do stuff


Running Helpers
===============

Single-file spider::


  # file: my-spider.py
  # imports omitted ...


  class MySpider(BaseSpider):
      # spider code ...


  if __name__ == '__main__':
      from scrapy_boilerplate import run_spider
      custom_settings = {
          # ...
      }
      spider = MySpider()

      run_spider(spider, custom_settings)


Single-file project with standard crawl command line options::


  # file: my-crawler.py
  # imports omitted ...


  class MySpider(BaseSpider):
      name = 'my_spider'
      # spider code ...


  class OtherSpider(CrawlSpider):
      name = 'other_spider'
      # spider code ...


  if __name__ == '__main__':
      from scrapy_boilerplate import run_crawler, SpiderManager
      custom_settings = {
          # ...
      }

      SpiderManager.register(MySpider)
      SpiderManager.register(OtherSpider)

      run_crawler(custom_settings)


.. note:: See the `examples`_ directory for working code examples.


.. _`Scrapy`: http://www.scrapy.org
.. _`PyQuery`: http://pypi.python.org/pypi/pyquery
.. _`examples`: https://github.com/darkrho/scrapy-boilerplate/tree/master/examples
