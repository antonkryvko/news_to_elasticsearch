#!/bin/env python3
"""
Downloads a list of urls for website to a file one at line.
"""

import json
import requests
from bs4 import BeautifulSoup

WEBSITE_URL = "https://lemberg-news.info"


def get_sequence_number_from_settings():
    with open('settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
    for elem, site in enumerate(settings['sites']):
        if site["url"] == WEBSITE_URL:
            return elem


def download_urls_to_file(sequence_number):
    with open('settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
    news_url = settings['sites'][sequence_number]['news_url']
    news_selector = settings['sites'][sequence_number]['news_selector']
    next_page_selector = settings['sites'][sequence_number]['next_page']
    pagination = settings['sites'][sequence_number]['pagination']
    if pagination == 'True':
        download_with_pagination(news_url, news_selector, next_page_selector)
    else:
        download_without_pagination(news_url, news_selector, next_page_selector)


def download_with_pagination(news_url, news_selector, next_page_selector):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/62.0.3202.9 Safari/537.36'}
    i = 1
    while True:
        try:
            next_page = '{0}{1}{2}'.format(news_url, next_page_selector, i)
            response = requests.get(next_page, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = soup.select(news_selector)
            urls_on_page = [
                urls[idx]['href'] if urls[idx]['href'].startswith('http') else WEBSITE_URL + urls[idx]['href'] for
                idx, _ in enumerate(urls)]
            print_urls_to_file(urls_on_page)
            print(next_page)
            i += 1
        except AttributeError:
            break
    print('News from {} downloaded.'.format(WEBSITE_URL))


def download_without_pagination(news_url, news_selector, next_page_selector):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/62.0.3202.9 Safari/537.36'}
    while True:
        try:
            response = requests.get(news_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = soup.select(news_selector)
            urls_on_page = [
                urls[idx]['href'] if urls[idx]['href'].startswith('http') else WEBSITE_URL + urls[idx]['href'] for
                idx, _ in enumerate(urls)]
            print_urls_to_file(urls_on_page)
            news_url = soup.select(next_page_selector)[0]['href']
            print(news_url)
        except requests.exceptions.MissingSchema:
            news_url = WEBSITE_URL + soup.select(next_page_selector)[0]['href']
        except IndexError:
            break
    print('News from {} downloaded.'.format(WEBSITE_URL))


def handle_exception_in_next_page_url(soup, news_url, next_page_selector):
    try:
        news_url = WEBSITE_URL + soup.select(next_page_selector)[0]['href']
    except requests.exceptions.MissingSchema:
        news_url = news_url + soup.select(next_page_selector)[0]['href']
    return news_url


def print_urls_to_file(urls_on_page):
    with open('urls.txt', 'a') as f:
        for url in urls_on_page:
            f.write(url + '\n')


if __name__ == '__main__':
    sequence_number = get_sequence_number_from_settings()
    download_urls_to_file(sequence_number)
