# Sample script for getting summary of a topic from wikipedia
# For more details https://github.com/goldsmith/Wikipedia
# This script requires wikipedia module. This can be installed by the command "pip install wikipedia"
# -*- coding: utf-8 -*-

import wikipedia
import sys
import json
import re
import urllib2
import re


if(len(sys.argv)>1):
	titles=sys.argv[1]
	wikipedia.set_lang("en")
	data = wikipedia.summary(titles)
	summary = data.split("\n")[0].encode('utf-8') # first paragraph

	#get wikipedia infobox image
	image_API="https://en.wikipedia.org/w/api.php?action=query&titles="+titles+"&prop=pageimages&format=json&pithumbsize=250"
	image= urllib2.urlopen(image_API).read()
	image_url=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', image)


	print json.dumps({"summary":summary,"image":image_url[0]}) 
	
