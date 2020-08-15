# News websites scraper
A scraper to get articles from news websites and store them into Elasticsearch database for further analysis.

Originally developed for Lviv and Dnipro local media sentiment analysis.

## Requirements
### Python
Script was written ant tested on python3.8, but should work on all python3 versions.
Create a virtual environment before you start:

`python3 -m venv env`

Then install required modules:

`pip3 install -r requirements.txt`


### Elasticsearch and Kibana
We shall use Elasticsearch as database due to its full-text search. Kibana is a frontend for Elasticsearch to make on
the fly analytics.
The best way to integrate them to your project is to use [Docker](https://github.com/deviantony/docker-elk).

## Usage
Before start, customize scraper according to your needs. Open `settings.json` and add a section with parameters of your
target:

* `url` - website address with protocol prefix and without / at the end;
* `news_url` - address of news section;
* `news_selector` - CSS-selector shows at article link;
* `next_page` - CSS-selector shows at next-page button or a relative path to the articles (whether you use pagination or
 common mode);
* `pagination` - a boolean flag which switches between pagination and common mode. Pagination mode is when you iterate
through article directory (ex. /page/1, page/2, page/n). Common mode uses when you "click" on next-page button. Which
mode to choose depends from you and website's layout;
* `title` - CSS-selector shows at article title;
* `date` - CSS-selector shows at date and time. In case it's impossible to determine appropriate selector, script takes
date from <meta> tag;
* `text` - CSS-selector shows at article text. Doesn't grab links and images.

Then enter website address, you've mentioned in `url` into `WEBSITE` variable in both `.py` files. It must be the same,
because it's used for linking settings. Enter Elasticsearch username and password into `ELASTIC_USER` and
`ELASTIC_PASSWORD` variable.

Doing this, start `download_urls.py`. It scrapes all links for article and stores them into `url.txt` file.
After script completion, start `download_articles.py`. It takes `FILE_WITH_URLS` variable, downloads pages by links and
stores its content into Elasticsearch. If Kibana was configured correctly, you would watch your data at port 5601.
