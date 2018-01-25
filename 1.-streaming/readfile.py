import codecs
from datetime import datetime
import json
import os
import string
import sys
import time

#Function: Read twitter Json answer, output user id 
def parse_json_tweet(line):
	tweet = json.loads(line)
	
	id= tweet['user']['id']
	#nfollowers = tweet['user']['followers_count']
	#nfriends = tweet['user']['friends_count']
	return [id]

'''start main'''

hashtag='cat'
file_name=hashtag+'.txt'
file_out=hashtag+'_participant.txt'
file_object  = open(file_name, "r")   
list_origin=[]

#Read lines of the file
for line in file_object:
	try:
		user = parse_json_tweet(line)
		list_origin.append(str(user[0]))

	except :
		pass
file_object.close()

seen = {}
#Delete the duplicates users
new_list = [seen.setdefault(x, x) for x in list_origin if x not in seen]
file  = open(file_out, "w")
for i in new_list:
	file.write("%s\n" % i)
file.close()