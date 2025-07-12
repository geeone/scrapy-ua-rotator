import os

from setuptools import setup, find_packages


path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(path, "requirements.txt")) as f:
    requirements = f.read().splitlines()

with open(os.path.join(path, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='scrapy-ua-rotator',
    version='1.0.0',
    author='Sergei Denisenko',
    author_email='sergei.denisenko@ieee.org',
    description='Flexible and modern User-Agent rotator middleware for Scrapy, supporting Faker, fake-useragent, and custom providers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/geeone/scrapy-ua-rotator',
    project_urls={
        'Documentation': 'https://github.com/geeone/scrapy-ua-rotator',
        'Source': 'https://github.com/geeone/scrapy-ua-rotator',
        'Bug Tracker': 'https://github.com/geeone/scrapy-ua-rotator/issues',
    },
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Framework :: Scrapy',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    license='MIT',
    python_requires='>=3.9',
    install_requires=requirements,
    keywords='scrapy user-agent middleware rotation fake-useragent faker providers proxy web-scraping',
)
