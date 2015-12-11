#!/usr/bin/env python
from __future__ import print_function
from sys import argv
import re
import json
import simplejson

Ftweets = []

def main():
	global Ftweets
	orig = 0
	dup = 0 
	tweetTexts = set()
	tweets = []
	fileList = open(argv[1],'r')
	for f in fileList:
		f = f.strip()
		text = open(f,'r').read()
		text = json.loads(text)
		tweets = tweets + text
	print(len(tweets))
	for twt in tweets:
	    tkey = 'text_' + twt['lang']
	    if twt['lang'] == 'en':
 		if twt['text_en_modified'] not in tweetTexts:
	           orig += 1
		   tweetTexts.add(twt[tkey])
		   tweetTexts.add(twt['text_en_modified'])
		   Ftweets.append(twt)
 	    elif twt[tkey] not in tweetTexts:
		orig += 1
		tweetTexts.add(twt[tkey])
		Ftweets.append(twt)
	    else:
		dup += 1
	print("orig: ", orig, " dup: ",dup)
	jData = simplejson.dumps(Ftweets, indent=4, skipkeys=True, sort_keys=True)
	fd = open('tweets.json','w')
	fd.write(jData)
	fd.close()

if __name__ == '__main__':
	main()
