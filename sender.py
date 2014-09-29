#!/usr/bin/python
import pickle
import sys
import hashlib
import smtplib
import datetime

def main(argv):

	filtered_listings={}

	#filter listings by paremters
	listings = pickle.load( open( Configuration.listings_db, "rb" ))
	for listing in listings:
		listing= listings.get(listing)
		if (listing['bezirk'] in Filter.Bezirks  
			and int(listing['price'])>Filter.MinPrice 
			and int(listing['price'])<=Filter.MaxPrice):
				filtered_listings[listing['hash']] =listing



	sent_items = pickle.load( open( Configuration.sent_items_db, "rb" ) )

	listing_to_send = {}
	for listing in filtered_listings:
		if listing not in sent_items:
			listing_to_send[listing] =filtered_listings.get(listing)

	message=""
	for listing in listing_to_send:
		listing= listing_to_send.get(listing)
		message +="""%s \n""" % (listing['url'])
	
  	sent_items = dict(sent_items.items() + listing_to_send.items())
	pickle.dump(sent_items, open( Configuration.sent_items_db, "wb" ))

	log('Sending mail')
  	log('Notifying about ' +str(len(listing_to_send)) + ' apartments!')

  	if(len(listing_to_send)>0):
		send_email(message.encode('utf-8'))

def send_email(message):
	FROM = Configuration.mail_sender
	TO = Configuration.mail_recivers
	SUBJECT = "Willhaben new apartments!!!"
	BODY = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, message)
	
	try:
		server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
		server.ehlo()
		server.starttls()
		server.login( Configuration.mail_sender, Configuration.mail_psw)
		server.sendmail(FROM, TO, BODY)
		server.close()
		log("Mail sent")
	except:
		log(str(sys.exc_info()[0]))
		log("Failed to send mail")

class Filter(object):
	MinPrice =0
	MaxPrice =900
	MinSize = -1
	MaxSize = -1
	Bezirks=['1070','1080','1090']

class Configuration(object):
	listings_db = 'willhaben.p'
	sent_items_db = 'willhaben_sent.p'
	mail_recivers = ['roko.bobic@gmail.com']
	mail_sender = 'roko.bobic@gmail.com'
	mail_psw = 'Codo5692'

def log(message):
	print str(datetime.datetime.utcnow()) + ' - ' + message

if __name__ == "__main__":
   main(sys.argv[1:])