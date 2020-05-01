#!/usr/bin/python
# scrapper.py is a script that will scrap ads from willhaben and save it into db. 
# Pages that are going to be scraped are defined in Configiration class 

import requests
import bs4
import sys
import re
import os
import urlparse
import json
import pickle
import time
import datetime
from decimal import *
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import selenium as se


def main(argv):

	#load existing listings
	pickle_listings = pickle.load( open( Configuration.pickle_db, "rb" ) )

	db_items_count = len(pickle_listings)
	
	options = webdriver.ChromeOptions()
	options.add_argument('--no-sandbox')
	options.add_argument('--headless')

	driver = webdriver.Chrome(chrome_options=options)
	
	for url in Configuration.categories:   		
		#parse all pages from given category
		listings = parse_category(url, driver)

	  	#add new listings into db
	  	for listing in listings:
	  		if listing not in pickle_listings:
	  			pickle_listings[listing]= listings.get(listing)

	#save listings
	pickle.dump(pickle_listings, open( Configuration.pickle_db, "wb" ))

	log('Fetched ' + str(len(pickle_listings)-db_items_count) + ' items')

def parse_category(category_url, driver):
	page = 1

	log(category_url)

	#parse first page
	listings = parse_page(category_url, driver)
	
	#contineue to parse if there is any result in first page
	pageExists = len(listings)>0
	while pageExists:
		#update url > replace old page with new
		category_url = category_url.replace('page=' + str(page), 'page=' + str(page+1))
		page= page+1

		log('fetch - ' + category_url)

		#parse next page
		current_page_listings = parse_page(category_url, driver)

  		log('results - ' + str(len(current_page_listings)))

		pageExists = len(current_page_listings)>0

		#merge current page into list
  		listings = dict(listings.items() + current_page_listings.items())

  	return listings

def parse_page(url, driver):
	try: 
		driver.get(url)
	except Exception as e:
		print(str(e))
			
	
	soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')	

	#select all listings from lise, execlude adds
	results = soup.select('#resultlist article[itemscope]')
	
	listings={}
	for result in results:
		listing = parse_listing(result)
		if listing is not type(None):
			hash = hashlib.sha224(listing['url']).hexdigest()
			listings[hash]=listing
	
	return listings

def parse_listing(result):
	listing={}
	number_pattern = re.compile(r'[0-9]+(\.[0-9]+)?')

	try:
		title = result.select('.header a')
		if title:
			listing['title'] =title[0].get_text()
			listing['url'] =  'http://www.willhaben.at' + title[0]['href']

		listing['size'] = -1
		size = result.select('.info .desc-left')[0].get_text().strip()
		if len(size)>0:
			if number_pattern.match(size):
				listing['size'] = number_pattern.search(size).group(0)

		listing['price'] = -1
		price = result.select('.content-section .info .pull-right')[0].get_text().strip().replace('.','').replace('.','')
		if len(price)>0 and number_pattern.match(price):
			listing['price'] = str(number_pattern.search(price).group(0))

		address = result.select('.address-lg')[0].get_text().replace("\r\n","").split()
		listing['bezirk'] = address[0]

		listing['created'] = str(datetime.datetime.utcnow())
	except Exception as e:
		print e
		print result
			

	return listing

class Configuration(object):
	pickle_db = 'willhaben.p'
	categories = [
				'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1010-innere-stadt?areaId=117223&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1020-leopoldstadt?areaId=117224&parent_areaid=900&page=1'
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1030-landstrasse?areaId=117225&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1040-wieden?areaId=117226&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1050-margareten?areaId=117227&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1060-mariahilf?areaId=117228&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1070-neubau?areaId=117229&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1080-josefstadt?areaId=117230&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1090-alsergrund?areaId=117231&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1100-favoriten?areaId=117232&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1110-simmering?areaId=117233&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1120-meidling?areaId=117234&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1130-hietzing?areaId=117235&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1140-penzing?areaId=117236&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1150-rudolfsheim-fuenfhaus?areaId=117237&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1160-ottakring?areaId=117238&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1170-hernals?areaId=117239&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1180-waehring?areaId=117240&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1190-doebling?areaId=117241&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1200-brigittenau?areaId=117242&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1210-floridsdorf?areaId=117243&parent_areaid=900&page=1',
				# 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1220-donaustadt?areaId=117244&parent_areaid=900&page=1',
				]

def log(message):
	print str(datetime.datetime.utcnow()) + ' - ' + message

if __name__ == "__main__":
   main(sys.argv[1:])