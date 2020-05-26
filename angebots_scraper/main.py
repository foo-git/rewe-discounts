#!/usr/bin/python3
"""
Scrapes the Rewe web pages for current discount offers and exports them as a beautiful markdown formatted list.
"""

import sys
import random
import time
import traceback
from datetime import datetime

from selenium import webdriver, common
from bs4 import BeautifulSoup


# user editable section
#
url_file = 'example-urls.txt'  # path to plain text file with one url per line
output_file = 'Angebote Rewe.md'  # path to output file
#
# ######################


def clean_string(input):
    """
    Replaces all newline characters in an input string with blank spaces.

    Args:
        input (str): Input string.

    Returns:
        output (str): Cleaned output string.

    """
    output = input.replace('\n', ' ').replace('\u2028', ' ').replace('\u000A', ' ')
    return output


def custom_exit(message, browser_running=False):
    print(message)
    # traceback.print_exc()
    if browser_running:
        browser.quit()
    sys.exit(1)


class Product:
    """
    Data-storage class for products.
    """
    def __init__(self):
        self._name = None
        self._price = None
        self._discount = None
        self._discount_valid = None
        self._normalized_price = None
        self._description = None
        self._category = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = clean_string(name)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = clean_string(price)

    @property
    def discount(self):
        return self._discount

    @discount.setter
    def discount(self, discount):
        self._discount = clean_string(discount)

    @property
    def discount_valid(self):
        return self._discount_valid

    @discount_valid.setter
    def discount_valid(self, discount_valid):
        self._discount_valid = clean_string(discount_valid)

    @property
    def normalized_price(self):
        return self._normalized_price

    @normalized_price.setter
    def normalized_price(self, normalized_price):
        self._normalized_price = clean_string(normalized_price).strip('(').strip(')')

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = clean_string(description)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        self._category = clean_string(category)


# load urls from file
urls = []
try:
    with open(url_file, 'r') as file:
        all_lines = file.readlines()
    urls = [url for url in all_lines if url.startswith('http')]
except FileNotFoundError:  # file not found or
    custom_exit('FAIL: URL file "{}" not found. '
                'Please check for typos or create it and write one url per line.'.format(url_file))

if not urls:
    custom_exit('FAIL: No URLs in file "{}" found. '
                'Only lines starting with "http" are processed as URLs.'.format(url_file))

# load web page and parse html
print('INFO: Loading pages ...')
page_soups = []
browser = webdriver.Firefox()
iteration = 0

for url in urls:
    iteration += 1
    try:
        print('INFO: Getting page {} of {} ...'.format(iteration, len(urls)))
        browser.get(url)
    except common.exceptions.InvalidArgumentException:
        custom_exit('FAIL: "{}" is not a valid URL. Check for typos and try again.'.format(url), browser_running=True)
    except common.exceptions.WebDriverException:
        custom_exit('FAIL: Could not retrieve web page "{}"'.format(url), browser_running=True)

    try:
        page_soups.append(BeautifulSoup(browser.page_source, features="lxml"))
    except:
        custom_exit('FAIL: Something went wrong during soup eating of "{}".'.format(url), browser_running=True)

    # sleep random time between 3s and 7s to prevent tripping DOS monitoring
    value = random.random()
    scaled_value = 3 + (value * (7-3))
    time.sleep(scaled_value)
browser.quit()


all_discounts = []
valid_date = None
separator = ' '  # description entries separator

# substrings to identify normalized prices in description
matches = ['g =', '100 g', 'l =', '100 ml', '100-g', '100-ml', '1-kg', 'je St.', '1 kg', '1-l', '-St.']

# stores product information from web page in a list grouped by categories
for soup in page_soups:
    category_discounts = []
    try:
        category = soup.find("h1").contents[0]
        valid_date = soup.find("span", class_="copy").contents[0]
        products = soup.find_all("div", class_="card-body")
        for item in products:
            NewProduct = Product()
            NewProduct.category = category
            try:
                NewProduct.discount_valid = item.find("p", class_="ma-offer-validfrom-to").contents[0]
            except IndexError:  # discount has no specific valid-from-to date
                NewProduct.discount_valid = ""
            NewProduct.name = item.find("p", class_="headline").contents[0].contents[0]
            NewProduct.price = item.find("div", class_="price").contents[0].contents[0]
            NewProduct.discount = item.find("div", class_="discount").contents[0].contents[0]

            # isolate normalized price and store the rest of information in description
            description = []
            for entry in item.find("div", class_="text-description").contents:
                try:
                    text = clean_string(entry.contents[0])
                    if any(x in text for x in matches):
                        NewProduct.normalized_price = text
                    else:
                        description.append(text)
                except IndexError:  # no description available
                    pass
            if not NewProduct.normalized_price:
                NewProduct.normalized_price = ''

            NewProduct.description = separator.join(description)
            category_discounts.append(NewProduct)
        all_discounts.append(category_discounts)
    except:
        custom_exit('FAIL: Unknown error during HTML feature extraction. '
                    'Maybe the web page "{}" has changed its source code?'.format(url))


# write product information grouped by categories to file
try:
    with open(output_file, 'w') as file:
        file.truncate(0)
        for category in all_discounts:
            header = "# {}\n{}\n\n".format(category[0].category, valid_date)
            file.write(header)
            for product in category:
                file.write("**{}**\n".format(product.name))
                file.write("- {}, {}\n".format(product.price, product.normalized_price))
                if product.description:
                    file.write("- {}\n".format(product.description))
                if product.discount_valid:
                    file.write("- {}\n".format(product.discount_valid))
                file.write('\n')
            file.write('\n')
        file.write("Update: {}".format(datetime.now()))
        print('OK: Wrote {} discounts to file "{}".'.format(sum([len(x) for x in all_discounts]), output_file))
except:
    custom_exit('FAIL: Something went wrong while writing to file "{}".'.format(output_file))
