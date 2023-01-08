#!/usr/bin/python3

'''
BackMarket price tracker and alerter
Set the 'price_wanted' and the 'false_positive_price' variables, see README for more informations
If you find any bugs, please report them under 'issues' in github

Note: Notify_run doesn't work with safari, for iOS devices, the next release will feature PushOver app support (https://pushover.net/) !

Made by 0xlazY !
'''

import requests, re
from notify_run import Notify
#from notify_run import Notify ## TODO


def get_currency(url):

    currency_dic = {
        '€': ['fr', 'es', 'it', 'de', 'be', 'at'],
        '$': ['com'],
        '£': ['uk'] ## co.uk
    }

    splited_url = url.split('.')
    #print(splited_url) ## debug
    
    if splited_url[3].split("/")[0] == 'uk':
        splited_url = 'uk'
    else:
        splited_url = splited_url[2].split("/")[0]
    #print(splited_url) ## debug
    if splited_url == 'at':
        country = 'at'
    else:
        country = 'com'

    currency_symbole = "$" ## default, if failed
    
    for key, value in currency_dic.items():
        if splited_url in value:
            currency_symbole = key

    #print(currency_symbole, country) ##Debug
    return currency_symbole, country


def get_webcontent(url):


    #Getting the URL and decoding it to allow for the prices to be found
    page = requests.get(url)
    content = page.content.decode()

    currency_symbole, country = get_currency(url)

    #Start of the pattern used for pricing within the HTML
    pattern = '<div class="body-2-light text-center text-primary-light">' + '\\n' + '      '

    if currency_symbole == '€' and country != 'at': ## If the symbol is at the end (Has the space as well)
        pattern +=  '[0-9]+' + '.' + '[0-9]+' + ' €'
    elif country == 'at':                           ## If within the 'at' region the euro is at the front
        pattern +=  '€' + '[0-9]+' + '.' + '[0-9]+'

    elif currency_symbole == '£':                   ##If within a 'uk' region pound is at the front
        pattern += '£' + '[0-9]+' + '.' + '[0-9]+'
    else:                                           ##Only leaves 'com' region with dollar at the front
        pattern += '$' + '[0-9]+' + '.' + '[0-9]+'

    raw_prices = re.findall(pattern, content) # Go through source and find the pattern noted above
    #print(raw_prices) ## debug

    price_lst = []

    for price in raw_prices:
        price = re.sub('<div class="body-2-light text-center text-primary-light">\\n      ', '', price) ##Removing any excess data, leaving only the price plus their currency symbol
                
        try: # because of potential problems when loading webpages and inconsistency, use 'try' before any index reference ([.])
            ##Going through same as before but removing the symbol to allow for it to be translated into a float for comparison
            if currency_symbole == '€' and country != 'at':
                parsed_price = re.sub(' €', '', price)
            elif country == 'at':
                parsed_price = re.sub('€', '', price)
            elif currency_symbole == '£': ## symbole before price
                parsed_price = re.sub('£', '', price)
            else:
                parsed_price = re.sub('$', '', price)

            parsed_price = float(parsed_price) ##Actually converting it here

            if parsed_price > false_positive_price:
                price_lst.append(parsed_price) # add the formated price to the price_lst
        except:
            print("Problem with parsing! {}".format(price))
    
    return price_lst, currency_symbole


def alerter(price_lst, currency_symbole):
    minimum_price = price_lst[0] # Initialize first minimum price

    for price in price_lst: # Gets the actual minimum price
        if price < minimum_price:
            minimum_price = price
    
    if minimum_price <= price_wanted:
        headers = {'Content-Type': 'text/text; charset=utf-8'} # needed to send specials char such as € ...
        data_text = '{}\'s price has drop to {}{} !'.format(device_name, minimum_price, currency_symbole)
        
        notify.send(data_text)
        requests.post(notify_run_url, data = data_text.encode('utf-8'), headers = headers) # Send POST request to notidy_run channel
    notify.send("Test Message using Python!")
    headers = {'Content-Type': 'text/text; charset=utf-8'} # needed to send specials char such as € ...
    requests.post(notify_run_url, data = "Test Message using Python!".encode('utf-8'), headers = headers) # Send POST request to notidy_run channel

    
def get_notify_run_url(config_file):
    conf = open(config_file, 'r')
    conf_url = conf.readline().strip()
    conf.close()

    return conf_url

def set_notify_run_url(config_file, notify_url):
    conf = open(config_file,'w')
    conf.truncate()
    conf.write(notify_url)



def main():
    for url in url_lst:
        #print(get_webcontent(url))
        price_lst, currency_symbole = get_webcontent(url)
        alerter(price_lst, currency_symbole)
        #print(price_lst)
        #print(currency_symbole)


if __name__ == '__main__':
    url_lst = ['https://www.backmarket.co.uk/en-gb/p/samsung-galaxy-note-20-ultra-5g-512-gb-black-unlocked/92afb688-6ece-4eab-afdf-5afa77242a54#l=11&scroll=false',]
#    url_lst = ['https://www.backmarket.co.uk/en-gb/p/iphone-se-2020-128-gb-black-unlocked/aa2db197-2380-4cbc-a55c-8c7df1df656c#l=10',]

    device_name = 'Samsung Galaxy Note20 Ultra 5G Dual Sim'
 
#    device_name = 'iPhone SE (2020)'

    # i.e, iPhone X 64gb Black

    notify_run_url = get_notify_run_url('config.cfg')
    
    if notify_run_url == "https://notify.run/XXXXXXXXXXXX":
        print("Creating a new channel!")
        notify = Notify()
        notify.register()
        set_notify_run_url('config.cfg', notify.endpoint)
    else:
        print("Opening channel already set in config file!")
        notify = Notify(endpoint=notify_run_url)


    # Create a notify_run channel and replace the url in config file (https://notify.run)
    ## TODO add channel creation with notidy_run module

    false_positive_price = 100 # Impossible price for the specified product
    price_wanted = 550 # Price of the product below which you want to receive a notification

    main()