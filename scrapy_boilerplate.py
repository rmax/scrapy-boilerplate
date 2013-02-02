"""Small set of utilities to simplify writing Scrapy spiders."""
import inspect
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
from scrapy.spider import BaseSpider
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


class CrawlSpider(_CrawlSpider):
    """Spider class with syntatic sugar to register rules and callbacks.

    Usage::

        class MySpider(CrawlSpider):
            pass

        MySpider.follow('next-page')

        @MySpider.rule('item\.php')
        def parse_item(response):
            # do stuff
            pass

    """

    # ensure an inmutable type for rules to avoid sharing the same
    # attribute with other instances/subclasses of this class
    rules = ()

    @classmethod
    def rule(cls, link_extractor, **params):
        """Decorator to associate a function as callback for given rule."""
        if isinstance(link_extractor, basestring):
            link_extractor = SgmlLinkExtractor(allow=link_extractor)
        def decorator(func):
            params['callback'] = func
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


def NewCrawlSpider(name, **params):
    """CrawlSpider dynamic factory.

    Usage::

        MySpider = NewCrawlSpider('my_spider')

    """
    base_cls = params.pop('base_cls', CrawlSpider)
    attrs = dict(base_cls.__dict__)
    attrs.update(name=name, **params)
    Spider = type('%s[%s]' % (base_cls.__name__, name), (base_cls,), attrs)
    # XXX: Scrapy requires that the spider __module__ value must be the
    # same as where module name where defined. In this case, the caller's
    # module.
    Spider.__module__ = inspect.currentframe().f_back.f_globals['__name__']
    return Spider


def spider_factory(url, name=None, base_cls=BaseSpider):
    """Decorator to transform a function into a spider class.

    The given function is used as default `parse` callback.

    Usage::

        @spider_factory('http://example.com', name='my_spider')
        def parse_example(response):
            # do stuff

    """
    def decorator(parse_func):
        attrs = {
            'name': name or parse_func.__name__,
            'start_urls': [url],
            'parse': lambda self, resp: parse_func(resp),
        }
        Spider = type('%s[%s]' % (base_cls.__name__, attrs['name']),
                      (base_cls,), attrs)
        # XXX: modify class's __module__ so scrapy can find it when using
        # default spider manager.
        Spider.__module__ = parse_func.__module__
        return Spider
    return decorator


def ItemFactory(names, base_cls=Item):
    """Creates an Item class with given fields specification.

    Usage::

        # create a item class with the fields: title, body and url.
        MyItem = ItemFactory('title body url')

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

