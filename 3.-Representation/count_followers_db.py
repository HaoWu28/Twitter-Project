import pymongo
from pymongo import MongoClient
import time
from datetime import datetime


def toCSV(text,file):
 	file = open(file,"a")
 	file.write("%s\n"%text)
 	file.close()

def searchdb(id_name,db):	
  cursor = db.find({"_id": id_name}, {"participated": "yes"})
  if (cursor.count()>0):
    return True
  else:
   return False


client = MongoClient()
db = client.fTestMdb_db
dbi= db.tweet

#file_name='tmp_csv.csv'


cursor = db.tweet.find({"participated":"yes"})
if (cursor.count()>0):
  for document in cursor:
   	count=0
   	lista=document['followers']
   	for follower in lista:
   			#print follower
   		if searchdb(follower,dbi):
   				#print('trobat')
   			count+=1 
   		#print count
   	try:
   		percentage=count/len(lista)
   		print (('%s,%s,%s,%s')%(str(document['_id']),str(count),str(len(lista)),str(percentage)))
   	except ZeroDivisionError:
   		percentage=0
   		print (('%s,0,0,0')%(str(document['_id'])))

    	
		
else:	
	print ("No results")
#os.remove(file_name)