import pymongo
from pymongo import MongoClient
import time
from datetime import datetime


def toCSV(text,file):
 	file = open(file,"a")
 	file.write("%s\n"%text)
 	file.close()

#Modify to the DB that you need
client = MongoClient()
db = client.fTestMdb_db
dbi= db.tweet


file_name='ts_R_csv.csv'
open(file_name, 'w').close()
#Search for the files in the DB that participated
cursor = db.tweet.find({"participated":"yes"})
if (cursor.count()>0):
  for document in cursor:
   	print ('%s,%s' %(str(document['_id']),len(document['tweets'])))
   	for tweets in document['tweets']:
		line=tweets
		#print line
		[tweet_id,date,timestamp,text]=str(line).split(':;:')
		#print timestamp
		toCSV(timestamp,file_name)	
else:	
	print ("No results")
#os.remove(file_name)