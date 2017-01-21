from collections import OrderedDict

from lxml import html
import requests
import pandas as pd

BASE_URL = 'https://www.indeed.com'


def build_url(url, *filters):
    return url + ''.join(['&' + param + '=' + val for param, val in filters])


def build_search_url(keywords, location):
    """

    :param keywords: job title, keywords or company
    :param location: city, state, or zip
    :return:
    """
    query = '/jobs?'
    keyword_filter = 'q', keywords
    location_filter = 'l', location
    date_filter = 'fromage', 'last'  # only get the latest postings
    url = BASE_URL + query
    return build_url(url, keyword_filter, location_filter, date_filter)


def posting_frame(posting_response):
    tree = html.fromstring(posting_response.text)
    posting_divs = tree.xpath('//div[contains(@itemtype,"JobPosting")]')
    posting_data = [_parse_job_posting(p) for p in posting_divs]
    return pd.DataFrame(posting_data)


def _parse_job_posting(job_posting):
    ru = './/a[contains(@title,"review") and contains(text(), "reviews")]/@href'
    col_paths = [
        ('title', './/h2[contains(@class,"jobtitle")]/a/@title'),
        ('url', './/h2[contains(@class,"jobtitle")]/a/@href'),
        ('date', './/span[contains(@class,"date")]/text()'),
        ('compensation', './/td[contains(@class,"snip")]/nobr/text()'),
        ('company', './/span[contains(@class,"company")]/span/text()'),
        ('location', './/span[contains(@class,"location")]//text()'),
        ('review_url', ru),
    ]
    pairs = [(k, _unique_strip(job_posting.xpath(v))) for k, v in col_paths]
    return OrderedDict(pairs)


def _unique_strip(values):
    if not values:
        return None
    if len(values) > 1:
        print(values)
    # assert(len(values) == 1)
    return values[0].strip()


if __name__ == '__main__':
    jobs_list = ['data scientist']

    salary = 160000
    keywords = 'data scientist ${:,d}'.format(salary)
    location = 'New York, NY'
    search_url = build_search_url(keywords=keywords, location=location)
    response = requests.get(search_url)
    indeed_df = posting_frame(response)

    # attrs = dict(cellpadding=0, cellspacing=0, border=0)
    # dfs = pd.read_html(response.text, attrs=attrs)

