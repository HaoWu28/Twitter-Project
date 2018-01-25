import pymongo
from pymongo import MongoClient

client = MongoClient()
#db = client.at_tweet_database
#db = client.finals_test_tweet_database
db = client.fTestMdb_db
#db = client.vagametro_tweet_database
dbi= db.tweet


#result = db.tweet.delete_many({"participated": "yes"})
#result = db.tweet.delete_many({"participated": "no"})
i=0
cursor = db.tweet.find({"participated":"yes"})
if (cursor.count()>0):
	for document in cursor:
  		print i
  		print((document['_id']))
  		i+=1
  		#for follower in document['followers']:
  		#	print follower
  		#for tweets in document ['tweets']:
  		#	print tweets
  	#i+=1 
      #print len(document ['grades'])
    	
    	#print document['tweets']	
    	#
    	#i+=1
	
else:	
	print "No results"