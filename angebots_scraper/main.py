#!/usr/bin/python3

from selenium import webdriver, common
import time
from bs4 import BeautifulSoup
import random
from datetime import datetime
import sys
import traceback

url_file = 'urls.txt'
output_file = 'Angebote Rewe.md'


class Product:
    def __init__(self):
        self.name = None
        self.price = None
        self.discount = None
        self.discount_valid = None
        self.normalized_price = None
        self.description = None
        self.category = None


with open(url_file, 'r') as file:
    urls = file.readlines()

page_soups = []

browser = webdriver.Firefox()
for url in urls:
    try:
        browser.get(url)
    except common.exceptions.WebDriverException:
        print("FAIL: Could not retrieve web page '{}'".format(url))
        traceback.print_exc()
        browser.quit()
        sys.exit(1)
    value = random.random()
    scaled_value = 3 + (value * (10-3))  # sleep random time between 3s and 10s
    time.sleep(scaled_value)
    try:
        page_soups.append(BeautifulSoup(browser.page_source, features="lxml"))
    except:
        print('FAIL: Something went wrong during soup eating of {}.'.format(url))
        traceback.print_exc()
        browser.quit()
        sys.exit(1)


browser.quit()

all_discounts = []
valid_date = None

separator = ' '

for soup in page_soups:
    try:
        category = soup.find("h1").contents[0]
        valid_date = soup.find("span", class_="copy").contents[0]
        products = soup.find_all("div", class_="card-body")
        category_discounts = []
        for item in products:
            NewProduct = Product()
            NewProduct.category = category
            try:
                NewProduct.discount_valid = item.find("p", class_="ma-offer-validfrom-to").contents[0].replace('\n', ' ')
            except IndexError:
                NewProduct.discount_valid = ""
            NewProduct.name = item.find("p", class_="headline").contents[0].contents[0].replace('\n', ' ')
            NewProduct.price = item.find("div", class_="price").contents[0].contents[0].replace('\n', ' ')
            NewProduct.discount = item.find("div", class_="discount").contents[0].contents[0].replace('\n', ' ')
            description = []
            for entry in item.find("div", class_="text-description").contents:
                try:
                    text = entry.contents[0].strip('\n')
                    if 'g =' in text or '100 g' in text or 'l =' in text or '100 ml' in text or '100-g' in text or '100-ml' in text or '1-kg' in text or 'je St.' in text or '1 kg' in text or '1-l' in text or '-St.' in text:
                        NewProduct.normalized_price = text.strip('(').strip(')')
                    else:
                        description.append(text)
                except IndexError:
                    pass
            if not NewProduct.normalized_price:
                NewProduct.normalized_price = ''

            NewProduct.description = separator.join(description)
            category_discounts.append(NewProduct)
        all_discounts.append(category_discounts)
    except:
        print('FAIL: Unknown error during HTML feature extraction. Maybe the web page {} has changed its source code?'.format(url))
        traceback.print_exc()
        sys.exit(1)

try:
    with open(output_file, 'w') as file:
        file.truncate(0)
        for category in all_discounts:
            header = "# {}\n{}\n\n".format(category[0].category, valid_date)
            file.write(header)
            for product in category:
                file.write("**{}**\n".format(product.name.strip('\n').replace('\u2028', ' ').replace('\u000A', ' ')))
                file.write("- {}, {}\n".format(product.price.strip('\n').replace('\u2028', ' ').replace('\u000A', ' '), product.normalized_price.strip('\n').replace('\u2028', ' ').replace('\u000A', ' ')))
                if product.description:
                    file.write("- {}\n".format(product.description.strip('\n').replace('\u2028', ' ').replace('\u000A', ' ')))
                if product.discount_valid:
                    file.write("- {}\n".format(product.discount_valid.strip('\n').replace('\u2028', ' ').replace('\u000A', ' ')))
                file.write('\n')
            file.write('\n')
        file.write("Update: {}".format(datetime.now()))
        print("OK: Wrote discounts to file.")
except:
    print('FAIL: Something went wrong while writing to file {}.'.format(output_file))
    traceback.print_exc()
    sys.exit(1)
