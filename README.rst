==================
scrapy-boilerplate
==================

`scrapy-boilerplate` is a small set of utilities for `Scrapy`_ to simplify
writing low-complexity spiders that are very common in small and one-off projects.

It requires `Scrapy`_ `(>= 0.16)` and has been tested using `python 2.7`.
Additionally, `PyQuery`_ is required to run the scripts in the `examples`_
directory.

.. note::

  The code is experimental, includes some magic under the hood and might be
  hard to debug. If you are new to `Scrapy`_, don't use this code unless
  you are ready to debug errors that nobody have seen before.


-----------
Usage Guide
-----------

Items
=====

Standard item definition:

.. code:: python

  from scrapy.item import Item, Field

  class BaseItem(Item):
      url = Field()
      crawled = Field()

  class UserItem(BaseItem):
      name = Field()
      about = Field()
      location = Field()

  class StoryItem(BaseItem):
      title = Field()
      body = Field()
      user = Field()

Becomes:

.. code:: python

  from scrapy_boilerplate import NewItem

  BaseItem = NewItem('url crawled')

  UserItem = NewItem('name about location', base_cls=BaseItem)

  StoryItem = NewItem('title body user', base_cls=BaseItem)


BaseSpider
==========

Standard spider definition:

.. code:: python

  from scrapy.spider import BaseSpider

  class MySpider(BaseSpider):
      name = 'my_spider'
      start_urls = ['http://example.com/latest']

      def parse(self, response):
          # do stuff


Becomes:

.. code:: python

  from scrapy_boilerplate import NewSpider

  MySpider = NewSpider('my_spider')

  @MySpider.scrape('http://example.com/latest')
  def parse(spider, response):
      # do stuff


CrawlSpider
===========

Standard crawl-spider definition:

.. code:: python

  from scrapy.contrib.spiders import CrawlSpider, Rule
  from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor


  class MySpider(CrawlSpider):
      name = 'my_spider'
      start_urls = ['http://example.com']

      rules = (
          Rule(SgmlLinkExtractor('category\.php'), follow=True),
          Rule(SgmlLinkExtractor('item\.php'), callback='parse_item'),
      )

      def parse_item(self, response):
          # do stuff


Becomes:

.. code:: python

  from scrapy_boilerplate import NewCrawlSpider

  MySpider = NewCrawlSpider('my_spider')
  MySpider.follow('category\.php')

  @MySpider.rule('item\.php')
  def parse_item(spider, response):
      # do stuff


Running Helpers
===============

Single-spider running script:

.. code:: python

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


Multi-spider script with standard crawl command line options:

.. code:: python

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
