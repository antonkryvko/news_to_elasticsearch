#!/bin/env python3
"""
Takes file with urls one at line and stores its content into Elasticsearch database.
"""

import json
import re

import newspaper
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from elasticsearch import Elasticsearch

WEBSITE_URL = ''
FILE_WITH_URLS = 'urls.txt'

ELASTIC_USER = 'elastic'
ELASTIC_PASSWORD = ''

es_client = Elasticsearch([{'host': 'localhost', 'port': 9200, 'http_auth': (ELASTIC_USER, ELASTIC_PASSWORD)}])
if es_client.ping():
    print('Connected to ELasticsearch')
else:
    print('Can\'t connect to Elasticsearch')


def get_sequence_number_from_settings():
    with open('settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
    for elem, site in enumerate(settings['sites']):
        if site["url"] == WEBSITE_URL:
            return elem


def download_articles(sequence_number):
    with open('settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
    title_selector = settings['sites'][sequence_number]['title']
    date_selector = settings['sites'][sequence_number]['date']
    text_selector = settings['sites'][sequence_number]['text']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 '
                      'Safari/537.36'}
    file_with_urls = open(FILE_WITH_URLS, 'r')
    url = True
    while url:
        try:
            url = file_with_urls.readline().rstrip()
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = regexps_clean(soup.select(title_selector)[0].get_text().strip())
            date, time = parse_date(url, soup, date_selector)
            text = regexps_clean(soup.select(text_selector)[0].get_text().strip())
        except (IndexError, newspaper.article.ArticleException):
            print('Сторінка видалена або не має дати публікації.')
            continue
        elastic_chulk = {"website": WEBSITE_URL, "url": url, "title": title, "date": date, "time": time, "text": text}
        es_client.index(index='local_news', body=elastic_chulk)
        print(elastic_chulk)
    file_with_urls.close()


def parse_date(url, soup, date_selector):
    months = {' січня': '/01', ' лютого': '/02', ' березня': '/03', ' квітня': '/04', ' травня': '/05',
              ' червня': '/06', ' липня': '/07', ' серпня': '/08', ' вересня': '/09', ' жовтня': '/10',
              ' листопада': '/11', 'грудня': '/12', ' января': '/01', ' февраля': '/02', ' марта': '/03',
              ' апреля': '/04',
              ' мая': '/05', ' июня': '/06', ' июля': '/07', ' августа': '/08', ' сентября': '/09', ' октября': '/10',
              ' ноября': '/11', 'декабря': '/12'}
    article = newspaper.Article(url)
    article.download()
    article.parse()
    date_time = article.publish_date
    if date_time is None:
        date_time = regexps_clean(soup.select(date_selector)[0].get_text().strip().lower())
        for month in months:
            if re.search(month, date_time):
                date_time = re.sub(month, months[month], date_time)
                break
        if re.search(r'\d{1,2}[./]\d{1,2}', date_time):
            date_time = re.search(r'(\d{1,2}:\d{2})*.*\d{1,2}[/.]\d{1,2}.*(\d{4}\s+)*(\d{1,2}:\d{2})*',
                                  date_time).group()
            print(date_time)
        date_time = parser.parse(date_time, dayfirst=True)
    date = date_time.date().strftime('%Y-%m-%d')
    time = date_time.time().strftime('%H:%M')
    return date, time


def regexps_clean(string):
    string = re.sub(r'\s{2,}', ' ', string)
    string = re.sub(r'\n', ' ', string).replace(u'\xa0', u' ')
    return string


if __name__ == '__main__':
    sequence_number = get_sequence_number_from_settings()
    download_articles(sequence_number)
