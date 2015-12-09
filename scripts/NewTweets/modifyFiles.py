#!/usr/bin/env python
from __future__ import print_function
from sys import argv
import re
import json
import simplejson

removeChars = ["(",")", "#",":", "!", "-"]
regexPatterns = ["RT","@.*","htt.*"]
tweets = []

def getSimpleText(text):
	global removeChars, regexPatterns
	line = text.split()
	for i in range(0,len(line)):
		line[i]
		for pattern in regexPatterns:
			if re.match(pattern,line[i]):
				line[i] = ''
				continue
		for ch in removeChars:
			line[i] = line[i].replace(ch,'')
	return ' '.join(line).strip()
	
def writeToFile():
	global tweets
	filename = argv[1].split('.')[0] +"_modified.json"
	try:
		jsondata = simplejson.dumps(tweets, indent=4, skipkeys=True, sort_keys=True)
		fd = open(filename, 'w')
		fd.write(jsondata)
		fd.close()
	except:
		print('ERROR writing',filename)
		pass

def main():
	global tweets
	tweetTexts  = set()
	text = open(argv[1],'r').read()
	text = json.loads(text)
	for twt in text:
		if twt['lang'] == 'ar' or twt['lang'] == 'tr':
			continue
		if 'text_en' in twt.keys():
			twt['text_en_modified'] = getSimpleText(twt['text_en'])

		tKey = 'text_' + twt['lang']
		if twt[tKey] not in tweetTexts:
			tweetTexts.add(twt[tKey])
			twt['topic'] = argv[2].strip()
			tweets.append(twt)
		else:
			print("duplicate",twt[tKey])
	writeToFile()

if __name__ == '__main__':
 	main()