#!/usr/bin/env python

#Imports required for App
from __future__ import print_function
import calendar
import sys
from datetime import date, timedelta 
import re
import json
import os.path
import tweepy
import codecs
import alchemy
import simplejson

#Global variables required through out the app
#Access Keys and tokens
consumer_key = None
consumer_secret = None
access_token = None
access_token_secret = None
tweepyAPI = None
tweetDict = {}
months = {v: k for k,v in enumerate(calendar.month_abbr)}
taggedDict = {}
dates = []
tweetCount = {'en':0, 'fr': 0, 'de': 0, 'ru' : 0 ,'ar' : 0 ,'tr' : 0}
entityTypes = ['Person', 'Country', 'Organization', 'Company', 'StateOrCounty', 'City', 'GeographicFeature', 'Region']
removeChars = ["(",")", "#",":" "-"]
regexPatterns = ["RT","@.*","htt.*"]
keys = [
	'bcae79f944a5cb0db0c70a8951776c3086478d09',
	'c906c5f952b6e30b619412f715441afb48b40595',
	'5759f13c51a2e85c1be4b3c056f9fc70cc63dec3',
	'fb47049cc0102f23024e98f10a975b7c8d0b328c',
	'3b807ba90afd0416a7f252bd24fd0873649fa0b9',
	'2be7047f2b028a60c305483f666dd2df404e7b8d',
	'4529e65dfb98e0f7a9f6f855ee96b5f456dbc28f'
	]


def setupDates(days):
   global dates
   for i in reversed(range(0,days)):
	dates.append((date.today()-timedelta(i)).strftime("%Y-%m-%d"))

# Setup various access keys and tokens from the user given input file 
def setupAuthKeys(authFile):
	global consumer_key, consumer_secret, access_token, access_token_secret
	if os.path.isfile(authFile) and os.access(authFile,os.R_OK):
		tokens = open(authFile, 'r').readlines()
		consumer_key = tokens[0].strip()
		consumer_secret = tokens[1].strip()
		access_token = tokens[2].strip()
		access_token_secret = tokens[3].strip()
	else:
		print("Auth file is missing or is not readable,exiting...")
		exit(1)

def setupTweepyAPI():
	global consumer_key, consumer_secret, access_token, access_token_secret, tweepyAPI
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	if auth:
		auth.set_access_token(access_token, access_token_secret)
		tweepyAPI = tweepy.API(auth,parser=tweepy.parsers.JSONParser())
	else:
		print("Authentication setup failed, exiting...")
		exit(1)

def getTweets(queryString):
    global tweepyAPI, dates, lang_geo, tweetCount
    count_max= 100
    # Querying for English tweets
    for i in range(len(dates)-1):
	 twtRes = []
         sDate = dates[i]
 	 eDate = dates[i+1]
	 for lng in tweetCount.keys():
	     tweets = tweepyAPI.search(q=queryString, \
	     include_entities=True, \
	     lang=lng, \
	     since=sDate, \
	     until=eDate, \
	     count=count_max,\
	     filter='retweets')
	     tweetCount[lng] += len(tweets['statuses'])
	     twtRes += tweets['statuses']
	 for tweet in twtRes:
             processTweet(tweet)
 	 writeTweetsToFile(queryString,sDate, eDate)
 	 
# Extract hashtags out of tweet
def processHashtags(tweet):
    hashtags = []
    if tweet.get('entities'):
       if tweet['entities'].get('hashtags'):
  	  tweet = tweet['entities']['hashtags']
	  if tweet and len(tweet) > 0:
	     for tag in tweet:
	         hashtags.append(tag['text'])
    return hashtags

# Extract Urls out of tweet
def processUrls(tweet):
	urls = []
	if tweet.get('entities'):
		if tweet['entities'].get('urls'):
			tweet = tweet['entities']['urls']
			if tweet and len(tweet) > 0:
				for url in tweet:
					urls.append(url['expanded_url'])
	return urls

# Extract entities from tagged data
def processEntities(taggedData):
	global entityTypes
	entities = []
	if taggedData.get('entities'):
		entity = taggedData['entities'];
		if entity and len(entity) > 0:
			for e in entity:
				if e['type'] in entityTypes:
					entities.append(e['text'])
	return entities

# Extract concepts from tagged data
def processConcepts(taggedData):
	concepts = []
	if taggedData.get('concepts'):
		concept = taggedData['concepts'];
		if concept and len(concept) > 0:
			for e in concept:
				concepts.append(e['text'])
	return concepts

def processDate(timeStamp):
	#   
	arr = timeStamp.split()
	year = arr[5]
	month = '0'+str(months[arr[1]])
	day = arr[2]
	dat = '-'.join([year,month,day])
	tim = arr[3].split('.')[0]
	return (dat+'T'+tim+'Z')

def getTag(text, id):
	global taggedDict, keys
	i = 0
	apikey = keys[i]
	data = alchemy.tagContent(apikey, text)
	if(data['status'] == 'ERROR'):
		i += 1
		if i == len(keys):
			print("End of keys, no new keys to try")
			return [],[]
		apikey = keys[i]
		data = alchemy.tagContent(apikey, text)
	tag = {}
	tag['id'] = id
	tag['concepts'] = processConcepts(data)
	tag['entities'] = processEntities(data)
	taggedDict[id] = tag
	return tag['concepts'], tag['entities']
	

def getSimpleText(txt):
   global removeChars, regexPatterns
   line = txt.split()
   try:
    for i in range(0,len(line)):
        line[i]
        for pattern in regexPatterns:
            if re.match(pattern,line[i]):
                line[i] = ''
                continue
        for ch in removeChars:
            line[i] = line[i].replace(ch,'')
	return ' '.join(line).strip()
   except:
    	print('Error in parsing: ', line)
    	pass
   return txt
   


#Process given tweet and extract all info
def processTweet(tweet):
	global tweetDict, taggedDict
	textKeyName = 'text_'
	twt = {}
	twt['id'] = tweet['id_str']
	twt['lang'] = tweet['lang']
	textKeyName += twt['lang']
	twt['topic'] = sys.argv[3]
	twt[textKeyName] = tweet['text'].encode('utf-8')
	if twt['lang'] == 'en':
		twt[textKeyName+'_modified'] = getSimpleText(tweet['text'])
	twt['tweet_hashtags'] = processHashtags(tweet)
	twt['tweet_urls'] = processUrls(tweet)
	twt['created_at'] = processDate(tweet['created_at'])
	twt['retweet_count'] = tweet['retweet_count']
	twt['favorite_count'] = tweet['favorite_count']
	twt['concepts'] , twt['entities'] = getTag(twt[textKeyName],twt['id'] )
	tweetDict[twt['id']] = twt

'''
def writeTagsToFile(fileName):
	global taggedDict
	f = codecs.open(fileName,'w','utf-8')
	f.write('[')
	tlist = taggedDict.values()
	tlen = len(tlist)-1
	for tweet in tlist:
		f.write(json.dumps(tweet))
		if(tlist.index(tweet) != tlen):
			f.write(",")
	f.write("]")
	f.close()
'''

def writeTweetsToFile(queryString, fromDate, toDate):
	global tweetDict
	outFileName = '_'.join(["tweets",queryString.replace(' ','_'), fromDate, toDate])
	f = codecs.open(outFileName+".json",'w','utf-8')
	tlist = tweetDict.values()
	tlen = len(tlist)-1
	jsondata = simplejson.dumps(tlist, indent=4, skipkeys=True, sort_keys=True)
	f.write(jsondata)
	f.close()

'''	for tweet in tlist:
		f.write(json.dumps(tweet))
		if(tlist.index(tweet) != tlen):
			f.write(",")
	f.write("]")
	f.close()
	raw = codecs.open(outFileName+"_raw"+".json",'w','utf-8')
	print(tlist,file=raw)
	raw.close()
	tweetDict = {}
	writeTagsToFile(outFileName+"_tagged.json")
'''

#Entry point
def main():		
	print(sys.argv)
	setupAuthKeys(sys.argv[1])
	setupTweepyAPI()
	setupDates(int(sys.argv[2]))
	queryString = ' '.join(sys.argv[4:])
	getTweets(queryString)
	for k,v in tweetCount.iteritems():
 	 	print(k,": ",v)

if __name__ == "__main__":
	main()
