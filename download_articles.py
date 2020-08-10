#!/bin/env python3
"""
Takes file with urls one at line and stores its content into Elasticsearch database.
"""

import json
import requests
from bs4 import BeautifulSoup

WEBSITE_URL = ''
FILE_WITH_URLS = 'urls.txt'


def get_sequence_number_from_settings():
    with open('settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
    for elem, site in enumerate(settings['sites']):
        if site["url"] == WEBSITE_URL:
            return elem


def download_article(sequence_number):
    with open('settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/62.0.3202.9 Safari/537.36'}
    file_with_urls = open(FILE_WITH_URLS, 'r')
    while True:
        url = file_with_urls.readline()
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')


if __name__ == '__main__':
    sequence_number = get_sequence_number_from_settings()
    download_article(sequence_number)