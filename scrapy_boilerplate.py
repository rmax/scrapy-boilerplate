"""Small set of utilities to simplify writing Scrapy spiders."""
import inspect
import itertools
import functools
import optparse
import sys

from scrapy import cmdline, log
from scrapy.commands.crawl import Command as CrawlCommand
from scrapy.commands.list import Command as ListCommand
from scrapy.contrib.spiders import Rule, CrawlSpider as _CrawlSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from scrapy.settings import CrawlerSettings
from scrapy.spider import BaseSpider as _BaseSpider
from scrapy.spidermanager import SpiderManager as _SpiderManager


class SpiderManager(_SpiderManager):
    """Spider manager class that allows to register spiders on runtime.

    This class is intended to be used along with the `run_crawler` function.
    """

    _spiders = {}

    def __init__(self):
        pass

    @classmethod
    def register(cls, spider_cls):
        """Register a spider class."""
        cls._spiders[spider_cls.name] = spider_cls

    @classmethod
    def from_crawler(cls, crawler):
        return cls()


class CallbackMixin(object):
    """Shared methods to register urls and callbacks.

    Usage::

        from scrapy.spider import BaseSpider

        class MySpider(CallbackMixin, BaseSpider):

            # override start requests to return only registered
            # requests with `scrape` decorator.
            def start_requests(self):
                return self.scrape_requests()


        # register an url with a callback for crawling
        @MySpider.scrape('http://example.com')
        def parse_item(spider, response):
            # do stuff

    """

    _scrape_urls = ()

    @classmethod
    def scrape(cls, url, **func_kwargs):
        """Decorator to specify to crawl an url with the decorated function."""

        def register_func(func):
            cls._scrape_urls += ((url, func, func_kwargs),)
            return func

        return register_func

    def scrape_requests(self):
        """Returns requests registered by `scrape` decorator."""
        for url, func, kwargs in self._scrape_urls:
            req = self.make_requests_from_url(url)
            req.callback = self.func_callback(func, **kwargs)
            yield req

    def func_callback(self, func, **kwargs):
        """Bind a function to this spider instance.

        Usage::

            from scrapy.spider import BaseSpider

            class MySpider(CallbackMixin, BaseSpider):

                # ...

                def parse(self, response):
                    # do stuff...
                    callback = self.func_callback(external_func)
                    return Request(url, callback=callback)

        """
        @functools.wraps(func)
        def callback(response):
            return func(spider=self, response=response, **kwargs)
        return callback


class BaseSpider(CallbackMixin, _BaseSpider):
    """Spider base class.

    Usage::

        class MySpider(BaseSpider):

            name = 'my_spider'
            start_urls = ['http://example.com']

            def parse(self, response):
                # do stuff


        # register additional pages

        @MySpider.scrape('http://example.org/company_info')
        def parse_info(spider, response):
            # do stuff


        @MySpider.scrape('http://example.org/gallery')
        def parse_images(spider, response):
            # do stuff

    """

    def start_requests(self):
        """Combine scrape and start requests."""
        return itertools.chain(CallbackMixin.scrape_requests(self),
                               _BaseSpider.start_requests(self))


class CrawlSpider(CallbackMixin, _CrawlSpider):
    """Spider class with syntatic sugar to register rules and callbacks.

    Usage::

        class MySpider(CrawlSpider):
            name = 'my_spider'
            start_urls = ['http://example.com']


        MySpider.follow('next-page')


        @MySpider.rule('item\.php')
        def parse_item(spider, response):
            # do stuff

    """

    # ensure an inmutable type for rules to avoid sharing the same
    # attribute with other instances/subclasses of this class
    rules = ()

    def _call_func(self, response, _func, **kwargs):
        """Simple callback helper to pass the spider instance to an external function."""
        return _func(spider=self, response=response, **kwargs)

    @classmethod
    def rule(cls, link_extractor, **params):
        """Decorator to associate a function as callback for given rule."""
        if isinstance(link_extractor, basestring):
            link_extractor = SgmlLinkExtractor(allow=link_extractor)

        def decorator(func):
            params['callback'] = '_call_func'
            params.setdefault('cb_kwargs', {})['_func'] = func
            cls.rules += (Rule(link_extractor, **params),)
            return func

        return decorator

    @classmethod
    def follow(cls, link_extractor, **params):
        """Method to register a callback-less follow rule."""
        params['follow'] = True
        if isinstance(link_extractor, basestring):
            link_extractor = SgmlLinkExtractor(allow=link_extractor)
        cls.rules += (Rule(link_extractor, **params),)

    def start_requests(self):
        """Combine scrape and start requests."""
        return itertools.chain(CallbackMixin.scrape_requests(self),
                               _CrawlSpider.start_requests(self))


def NewSpider(name, **params):
    """Create a new subclass of BaseSpider or given base_cls.

    Usage::

        MySpider = NewSpider('my_spider')
    """
    base_cls = params.pop('base_cls', BaseSpider)
    attrs = dict(base_cls.__dict__)
    attrs.update(name=name, **params)
    Spider = type('%s[%s]' % (base_cls.__name__, name), (base_cls,), attrs)
    # XXX: modify class's __module__ so scrapy can find it when using
    # default spider manager.
    Spider.__module__ = inspect.currentframe().f_back.f_globals['__name__']
    return Spider


NewCrawlSpider = functools.partial(NewSpider, base_cls=CrawlSpider)
NewCrawlSpider.__doc__ = """Create a new subclass of CrawlSpider.
    Usage::

        MySpider = NewCrawlSpider('my_spider')
    """


def NewItem(names, base_cls=Item):
    """Creates an Item class with given fields specification.

    Usage::

        BaseItem = NewItem('title body url')

        QuestionItem = NewItem('tags status', base_cls=BaseItem)

        AnswerItem = NewItem('user', base_cls=BaseItem)

    """
    if isinstance(names, basestring):
        names = names.split()
    attrs = dict((name, Field()) for name in names)
    return type('%s[%s]' % (base_cls.__name__, ' '.join(names)),
                (base_cls,), attrs)


def run_spider(spider, settings=None):
    """Run a spider instance through the scrapy crawler.

    This function is suitable for standalone scripts.
    """
    crawler = CrawlerProcess(_build_settings(settings))
    crawler.install()
    crawler.configure()
    log.start_from_crawler(crawler)
    crawler.crawl(spider)
    crawler.start()


def run_crawler(argv=None, settings=None):
    """Run the scrapy crawler bounded to registered spiders.

    This function is suitable for standalone scripts.

    Usage::

        # mimic 'scrapy crawl' command having these two spiders available
        SpiderManager.register(FooSpider)
        SpiderManager.register(BarSpider)

        run_crawler()

    """
    argv = argv or sys.argv
    settings = _build_settings(settings)

    # load spider manager from this module
    settings.overrides.update({
        'SPIDER_MANAGER_CLASS': '%s.%s' % (__name__, SpiderManager.__name__),
    })

    crawler = CrawlerProcess(settings)
    crawler.install()

    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter())
    parser.add_option('-l', '--list', action='store_true',
                      help="List available spiders")

    cmd = CrawlCommand()
    settings.defaults.update(cmd.default_settings)
    cmd.settings = settings
    cmd.add_options(parser)

    parser.usage = "%s %s" % (argv[0], cmd.syntax())
    opts, args = parser.parse_args()
    if opts.list:
        settings.defaults.update(ListCommand.default_settings)
        listcmd = ListCommand()
        listcmd.set_crawler(crawler)
        listcmd.run(args, opts)
        sys.exit(listcmd.exitcode)
    else:
        cmdline._run_print_help(parser, cmd.process_options, args, opts)
        cmd.set_crawler(crawler)
        cmdline._run_print_help(parser, cmdline._run_command, cmd, args, opts)
        sys.exit(cmd.exitcode)


def _build_settings(settings=None):
    if settings is None:
        settings = CrawlerSettings()
    elif isinstance(settings, dict):
        values = settings
        settings = CrawlerSettings()
        settings.defaults.update(values)
    return settings
