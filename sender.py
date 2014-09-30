#!/usr/bin/python
import pickle
import sys
import hashlib
import smtplib
import datetime

def main(argv):
	gmailPass = argv[0]
	
	filtered_listings={}

	#load listings
	listings = pickle.load( open( Configuration.listings_db, "rb" ))
	
	#filter listings by paremters
	for listing in listings:
		hash = listing
		listing= listings.get(listing)
		if (listing['bezirk'] in Filter.Bezirks  
			and int(listing['price'])>Filter.MinPrice 
			and int(listing['price'])<=Filter.MaxPrice):
				filtered_listings[hash] =listing


	#laod sent items		
	sent_items = pickle.load( open( Configuration.sent_items_db, "rb" ) )

	#find matched apartment that arent sent in email yet
	listing_to_send = {}
	for listing in filtered_listings:
		if listing not in sent_items:
			listing_to_send[listing] =filtered_listings.get(listing)

	#construct list of urls
	message=""
	for listing in listing_to_send:
		listing= listing_to_send.get(listing)
		message +="""%s \n""" % (listing['url'])
	
	log('Sending mail')
  	log('Notifying about ' +str(len(listing_to_send)) + ' apartments!')

	#send email
	if(len(listing_to_send)>0):
		send_email(message.encode('utf-8'),gmailPass)

	#merge sent items and save them to db
  	sent_items = dict(sent_items.items() + listing_to_send.items())
	pickle.dump(sent_items, open( Configuration.sent_items_db, "wb" ))


def send_email(message,gmailPass):
	FROM = Configuration.mail_sender
	TO = Configuration.mail_recivers
	SUBJECT = "Willhaben new apartments!!!"
	BODY = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, message)
	
	try:
		server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
		server.ehlo()
		server.starttls()
		server.login( Configuration.mail_sender, gmailPass)
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
	Bezirks=['1010','1020','1030','1040','1050','1060','1070','1080','1090','1150']

class Configuration(object):
	listings_db = 'willhaben.p'
	sent_items_db = 'willhaben_sent.p'
	mail_recivers = ['roko.bobic@gmail.com']
	mail_sender = 'roko.bobic@gmail.com'
	
def log(message):
	print str(datetime.datetime.utcnow()) + ' - ' + message

if __name__ == "__main__":
   main(sys.argv[1:])