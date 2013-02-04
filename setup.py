import os
from setuptools import setup

LONG_DESC = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()


setup(
    name='scrapy-boilerplate',
    version='0.2.1',
    description='Small set of utilities to simplify writing Scrapy spiders.',
    long_description=LONG_DESC,
    author='Rolando Espinoza La fuente',
    author_email='darkrho@gmail.com',
    url='https://github.com/darkrho/scrapy-boilerplate',
    py_modules=['scrapy_boilerplate'],
    license='BSD',
    install_requires=['Scrapy>=0.16'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
)
