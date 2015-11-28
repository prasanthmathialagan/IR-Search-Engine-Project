# -*- coding: utf-8 -*-

import json
import urllib2 
import detectlanguage
from textblob import TextBlob


detectlanguage.configuration.api_key = "4a34be079e10fe1aa3fd334e8de3434c"


queries_file=open("data/queries.txt")
queries=queries_file.read().split("\n")

queries_file.close()
outfn = 'trec/trec.txt'
outf = open(outfn, 'w')

IRModel='default'

native_boost=1
foreign_boost=0.8
default_HT_boost=0.5
HT_boost=1

for query in queries:
	(qid,q)=query.split(' ',1)
	blob = TextBlob(q)
	try:
		q_en= str(blob.translate(to="en"))
	except:
		q_en=q

	try:	
		q_ru= str(blob.translate(to="ru"))
	except:
		q_ru=q	

	try:	
		q_de= str(blob.translate(to="de"))
	except:
		q_de=q	

	print q_en
	print q_de
	print q_ru
	print "----"

	lang=detectlanguage.detect(q)
	lang= lang[0]["language"]
	if lang=="en" :
		text_en_boost=native_boost
		text_de_boost=foreign_boost
		text_ru_boost=foreign_boost
		hashtags_boost=default_HT_boost
	elif lang=="ru" :
		text_en_boost=foreign_boost
		text_de_boost=foreign_boost
		text_ru_boost=native_boost
		hashtags_boost=default_HT_boost

	elif lang=="de" :
		text_en_boost=foreign_boost
		text_de_boost=native_boost
		text_ru_boost=foreign_boost
		hashtags_boost=default_HT_boost
	else:
		text_en_boost=native_boost
		text_de_boost=native_boost
		text_ru_boost=native_boost
		hashtags_boost=HT_boost

	query_in_all_languages='text_en:('+q_en+')^'+str(text_en_boost)+' OR '+'text_de:('+q_de+')^'+str(text_de_boost)+' OR '+'text_ru:('+q_ru+')^'+str(text_ru_boost)+' OR '+'tweet_hashtags:('+q_en+')^'+str(hashtags_boost)
	#print query_in_all_languages



	inurl = 'http://abi93k.koding.io:8983/solr/partb/select?q='+urllib2.quote(query_in_all_languages)+'&fl=id%2Cscore&wt=json&indent=true&rows=2147483647'

	

	
	data = urllib2.urlopen(inurl)

	json_data=json.load(data)
	rq=json_data["responseHeader"]["params"]["q"]
	print str(json_data['response']['numFound']) +" document(s) found for query "+str(qid) +" "+q
	docs = json_data['response']['docs']
	# the ranking should start from 1 and increase
	rank = 1
	for doc in docs:
		outf.write(qid + ' ' + 'Q0' + ' ' + str(doc['id']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
		rank += 1
	
	


outf.close()
