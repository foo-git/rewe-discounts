#!/usr/bin/python3

import requests
import datetime

output_file = 'Angebote Rewe API.md'  # path to output file
url = 'https://mobile-api.rewe.de/products/offer-search'


class Product:
    """
    Data-storage class for products.
    """
    def __init__(self):
        self._name = None
        self._price = None
        self._discount = None
        self._discount_valid = None
        self._base_price = None
        self._description = None
        self._category = None
        self._currency = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = price

    @property
    def discount(self):
        return self._discount

    @discount.setter
    def discount(self, discount):
        self._discount = discount

    @property
    def discount_valid(self):
        return self._discount_valid

    @discount_valid.setter
    def discount_valid(self, discount_valid):
        self._discount_valid = discount_valid

    @property
    def base_price(self):
        return self._base_price

    @base_price.setter
    def base_price(self, base_price):
        self._base_price = base_price.strip('(').strip(')')

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category_id):
        self._category = categories_dict[category_id[0]]

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, currency):
        self._currency = currency


response = requests.get(url).json()
valid_date = response['_meta']['offerDuration']['label']
discounts = response['items']

# reformat categories for easier access
categories = response['_meta']['categories']
categories_dict = {}
categorized_products = {}
for n in range(0, len(categories)):
    categories_dict.update({categories[n]['id']: categories[n]['name']})
    categorized_products.update({categories[n]['id']: []})


all_discounts = []
for item in discounts:
    NewProduct = Product()
    NewProduct.name = item['name']
    try:
        NewProduct.base_price = item['basePrice']
    except KeyError:
        NewProduct.base_price = item['quantityAndUnit']
    NewProduct.price = item['price']
    NewProduct.currency = item['currency']
    NewProduct.category = item['categoryIDs']
    try:
        NewProduct.description = item['quantityAndUnit'] + item['additionalInformation']
    except KeyError:
        NewProduct.description = item['quantityAndUnit']

    categorized_products[item['categoryIDs'][0]].append(NewProduct)

print('foo')

with open(output_file, 'w') as file:
    file.truncate(0)
    for category_id in categorized_products:
        header = "# {}\n{}\n\n".format(categories_dict[category_id], valid_date)
        file.write(header)
        for product in categorized_products[category_id]:
            file.write("**{}**\n".format(product.name))
            file.write("- {}, {}\n".format(product.price, product.base_price))
            if product.description:
                file.write("- {}\n".format(product.description))
            if product.discount_valid:
                file.write("- {}\n".format(product.discount_valid))
            file.write('\n')
        file.write('\n')
    file.write("Update: {}".format(datetime.datetime.now()))
    print('OK: Wrote {} discounts to file "{}".'.format(sum([len(categorized_products[x]) for x in categorized_products]), output_file))
