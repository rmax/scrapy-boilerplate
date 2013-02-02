from setuptools import setup

setup(name='scrapy-boilerplate',
      version='0.1',
      description='Small set of utilities to simplify writing Scrapy spiders.',
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
