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
		print(f)
		text = open(f,'r').read()
		#print(text)
		text = json.loads(text)
		#print(text)
		tweets = tweets + text
	print(len(tweets))
	for twt in tweets:
		tKey = 'text_' + twt['lang']
		if twt[tKey] not in tweetTexts:
			orig += 1
			tweetTexts.add(twt[tKey])
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