#!/usr/bin/python3

import sys
import argparse
import datetime
import traceback

import cloudscraper


class Product:
    """
    Data-storage class for products.
    """

    def __init__(self):
        self._name = ''
        self._price = ''
        self._discount = ''
        self._discount_valid = ''
        self._base_price = ''
        self._description = ''
        self._category = ''
        self._currency = ''

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
        if price is str:
            self._price = clean_string(price).replace('.', ',')
        else:
            self._price = str(price).replace('.', ',')

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
    def base_price(self):
        return self._base_price

    @base_price.setter
    def base_price(self, base_price):
        self._base_price = clean_string(base_price).strip('(').strip(')')

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
    def category(self, category_id):
        self._category = clean_string(categories_id_mapping[category_id[0]])

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, currency):
        self._currency = clean_string(currency)


def clean_string(input):
    """
    Replaces all newline characters in an input string with blank spaces.

    Args:
        input (str): Input string.

    Returns:
        output (str): Cleaned output string.

    """
    output = input.replace('\n', ' ').replace('\u2028', ' ').replace('\u000A', ' ').rstrip().lstrip()
    return output


def custom_exit(message):
    print(message)
    # traceback.print_exc()
    sys.exit(1)


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Fetches current Rewe discount offers for a specific market.',
    epilog=
    'Example usages:\n'
    ' - Prints the market IDs of all Rewe markets in/near the zip code/PLZ "63773":\n'
    '      rewe_discounts.py --list-markets 63773\n'
    ' - Exports current discounts of the market with the ID "562286":\n'
    '      rewe_discounts.py --market-id 562286 --output-file "Angebote Rewe.md"\n'
    ' - Exports current discounts of the market with the ID "562286" and highlights defined products:\n'
    '      rewe_discounts.py --market-id 562286 --output-file "Angebote Rewe.md" --highlights=highlights.txt'
)

parser.add_argument('--market-id', type=str, help='Market ID, needs to be obtained by executing --list-markets.')
parser.add_argument('--output-file', type=str, help='Output file path.')
parser.add_argument('--highlights', type=str, help='Products mentioned in this file, e.g. "Joghurt", '
                                                   'are highlighted in the output file.')
parser.add_argument('--list-markets', type=str, help='Given the zip code (PLZ), list all markets and their ID.')
args = parser.parse_args()
market_id = args.market_id
output_file = args.output_file
highlight_file = args.highlights

scraper = cloudscraper.create_scraper()


# Here we differentiate between mode "print market IDs" and mode "print offers of selected market"
if args.list_markets:  # mode "print market IDs"
    try:
        assert int(args.list_markets)
        assert len(args.list_markets) == 5
    except (ValueError, AssertionError):
        custom_exit('FAIL: Unrecognized input "{}". Please provide a 5 digit postal code.'.format(args.list_markets))
    zip_code = args.list_markets

    # Craft query and load JSON stuff.
    url = 'https://shop.rewe.de/mc/api/markets-stationary/' + zip_code
    try:
        data = scraper.get(url).json()
    except:  # might be refined later on
        custom_exit('FAIL: Unknown error while fetching discounts from {}. '
                    'Maybe a typo or the server rejected the request.'.format(url))
    markets = data['stationaryMarkets']

    if not markets:
        custom_exit('FAIL: No markets found near provided zip code "{}".'.format(zip_code))

    print('  ID     Location')
    for market in markets:
        print('{}: {}, {} {}, {} {}'.format(market['id'], market['name'], market['address']['street'],
                                            market['address']['houseNumber'], market['address']['postalCode'],
                                            market['address']['city']))
    print('\nPlease choose the right market and its ID from above.\n\n'
          'Example program call to fetch all discounts from a market:\n'
          '  rewe_discounts.py --market-id ID --output-file "Angebote Rewe.md"')

    sys.exit(0)

else:  # mode "print offers of selected market"
    if not market_id or not output_file:
        parser.print_help()
        sys.exit(0)
    try:
        assert int(market_id)
        assert len(market_id) == 6
    except (ValueError, AssertionError):
        custom_exit('FAIL: Unrecognized input "{}". Please provide a 6 digit market ID.'.format(args.market_id))

    # Craft query and load JSON stuff.
    url = 'https://mobile-api.rewe.de/products/offer-search?categoryId=&marketId=' + market_id
    try:
        data = scraper.get(url).json()
    except:
        custom_exit('FAIL: Unknown error while fetching discounts from {}. '
                    'Maybe a typo or the server rejected the request.'.format(url))

    # Reformat categories for easier access. ! are highlighted products, and ? are uncategorized ones.
    # Order of definition here determines printing order later on.
    categories = data['_meta']['categories']
    categories_id_mapping = {'!': 'Vorgemerkte Produkte'}
    categorized_products = {'!': []}
    for n in range(0, len(categories)):
        categories_id_mapping.update({categories[n]['id']: categories[n]['name']})
        categorized_products.update({categories[n]['id']: []})
    categories_id_mapping.update({'?': 'Unbekannte Kategorie'})
    categorized_products.update({'?': []})

    # Check and process highlights file
    product_highlights = []
    if highlight_file:
        try:
            with open(highlight_file, 'r') as file:
                all_lines = file.readlines()
            product_highlights = [item.strip('\n') for item in all_lines if not item.startswith('#') and item.strip('\n')]
        except FileNotFoundError:  # file not found or
            custom_exit('FAIL: Highlights file "{}" not found. '
                        'Please check for typos or create it and write one url per line.'.format(highlight_file))
        if not product_highlights:
            print('WARNING: No product highlights in file "{}" found. '
                  'Ignoring user request to highlight and continuing anyway.'.format(highlight_file))

    # Stores product data in a dict with categories as keys for a sorted printing experience.
    # Sometimes the data from Rewe is mixed/missing, so that's why we need all those try/excepts.
    for item in data['items']:
        NewProduct = Product()
        NewProduct.name = item['name']
        NewProduct.price = item['price']
        NewProduct.currency = item['currency']
        try:
            NewProduct.category = item['categoryIDs']
        except KeyError:  # if category not defined in _meta, assign to unknown category
            NewProduct.category = '?'
        try:
            NewProduct.base_price = item['basePrice']
        except KeyError:  # sometimes the basePrice is written in quantityAndUnit
            NewProduct.base_price = item['quantityAndUnit']
        try:
            NewProduct.discount = item['discount']
        except KeyError:  # sometimes no discount is given per product
            NewProduct.discount = ''
        try:
            NewProduct.description = item['quantityAndUnit'] + ' ' + item['additionalInformation']
        except KeyError:  # sometimes additionalInformation is missing
            NewProduct.description = item['quantityAndUnit']

        # Move product into the respective category list ...
        try:
            categorized_products[item['categoryIDs'][0]].append(NewProduct)
        except KeyError:
            categorized_products['?'].append(NewProduct)
        # ... but highlighted products are the only ones in two categories
        if any(x in NewProduct.name for x in product_highlights):
            categorized_products['!'].append(NewProduct)

    # Writes product list grouped by categories to file, and cleans file first
    with open(output_file, 'w') as file:
        file.truncate(0)
        offers_valid_date = data['_meta']['offerDuration']['label']
        for category_id in categorized_products:
            if category_id == '!':
                header = '# {}\n{}\n\n'.format(categories_id_mapping[category_id], offers_valid_date)
            else:
                header = '# {}\n\n'.format(categories_id_mapping[category_id])
            file.write(header)
            for product in categorized_products[category_id]:
                file.write('**{}**\n'.format(product.name))
                file.write('- {}, {}\n'.format(product.price, product.base_price))
                file.write("- {}\n".format(product.description))
                if product.discount_valid:
                    file.write("- {}\n".format(product.discount_valid))
                file.write('\n')
            file.write('\n')
        file.write("Update: {}".format(datetime.datetime.now()))

    if product_highlights:
        print('OK: Wrote {} discounts to file "{}" and highlighted {}.'.format(
            sum([len(categorized_products[x]) for x in categorized_products]) - len(categorized_products['!']),
            output_file,
            sum([len(categorized_products['!'])])))
    else:
        print('OK: Wrote {} discounts to file "{}".'.format(
            sum([len(categorized_products[x]) for x in categorized_products]), output_file))
    sys.exit(0)