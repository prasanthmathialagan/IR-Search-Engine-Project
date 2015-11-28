import urllib2
import json

# apikey = "bcae79f944a5cb0db0c70a8951776c3086478d09"
# text = "The more things change... Yes, I'm inclined to agree, especially with regards to the historical relationship between stock prices and bond yields. The two have generally traded together, rising during periods of economic growth and falling during periods of contraction. Consider the period from 1998 through 2010, during which the U.S. economy experienced two expansions as well as two recessions: Then central banks came to the rescue. Fed Chairman Ben Bernanke led from Washington with the help of the bank's current $3.6T balance sheet. He's accompanied by Mario Draghi at the European Central Bank and an equally forthright Shinzo Abe in Japan. Their coordinated monetary expansion has provided all the sugar needed for an equities moonshot, while they vowed to hold global borrowing costs at record lows."
# outputmode = "json"

# Tags the given text with entities and concepts from Alchemy API and returns a JSON data.
def tagContent(apikey, text):
       baseurl = "http://gateway-a.watsonplatform.net/calls/text/TextGetCombinedData?"
       url = baseurl + "apikey=" + apikey + "&extract=entities,concepts&outputMode=json&text=" + urllib2.quote(text)
       print(url)
       data = urllib2.urlopen(url)
       json_data=json.load(data)
       return json_data

# text = "The more things change... Yes, I'm inclined to agree, especially with regards to the historical relationship between stock prices and bond yields. The two have generally traded together, rising during periods of economic growth and falling during periods of contraction. Consider the period from 1998 through 2010, during which the U.S. economy experienced two expansions as well as two recessions: Then central banks came to the rescue. Fed Chairman Ben Bernanke led from Washington with the help of the bank's current $3.6T balance sheet. He's accompanied by Mario Draghi at the European Central Bank and an equally forthright Shinzo Abe in Japan. Their coordinated monetary expansion has provided all the sugar needed for an equities moonshot, while they vowed to hold global borrowing costs at record lows."
# output = tagContent("bcae79f944a5cb0db0c70a8951776c3086478d09",text);
# print(output["entities"]);