# coding=utf-8
import os
import tweepy
from tweepy import OAuthHandler
import time
from datetime import datetime
import pymongo
from pymongo import MongoClient
import re

#Twitter API keys
consumer_key = '--- Your KEY---'
consumer_secret = '--- Your KEY---'
access_token = '--- Your KEY---'
access_secret = '--- Your KEY---'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

# Data to modify: input filename and dates
nom='testMDB'
date_orig='7/1/2017' #example 12/30/2017
date_fin='9/20/2017'


# Data to modify: hashtag
hasht1='#testMDB'

hasht=[hasht1]

 
#Temporal files and csv files for Ghepi

file_orig=nom+'_participant.txt'
file_tmp=nom+'_tmp.txt'
file_tmp2=nom+'nodes.csv'
file_tmp3=nom+'edges.csv'

#Database data - MongoDB
client = MongoClient()

db = client.fTestMdb_db
dbi= db.tweet

#Database functions
#Create input of new user to database
def insertdb(id_name,participated,followers,tweet,db):
	#tweets=tweet 
	result = db.insert_one(
       {
           "_id":id_name,
           "participated":participated,
           "followers":followers,
           "tweets": [tweet]
       }
   )
#Update info of user in database
def updatedb(id_name,tweet,db): 
    db.update({"_id":id_name}, {'$push': {'tweets': tweet}})

#Search if exist in the database
def searchdb(id_name,db):	
  cursor = db.find({"_id": id_name})
  if (cursor.count()>0):
    return True
  else:
   return False

#Error Functions
def is_rate_limit_error(e):
	return isinstance(e.message, list) \
		and e.message[0:] \
		and 'code' in e.message[0] \
		and e.message[0]['code'] == 88

#Program functions

#From an twitter id return a twitter screen name
def idToSName(id):
	user_Name = api.get_user(id)
	return user_Name.screen_name

#Function writes to the end of a file
def toFile(text,file):
 	file = open(file,"a")
 	try:
 		tweet=text.rstrip()
 	except AttributeError: 
 		tweet=text
 	file.write("%s\n"%tweet)
 	file.close()

#Function search if there are some hashtag in the users tweet
def multiplematch(hashtag,text):
	trobat = False
	i=0
	while (i<len(hashtag) and not trobat):
		if hashtag[i] in text:
			trobat=True
		i+=1
	return trobat

#Funtion that creates the temporal files and the csv files
def init_files(tmp,tmp2,tmp3):
	open(tmp, 'w').close()
	open(tmp2, 'w').close()
	open(tmp3, 'w').close()
	toFile('id;user',tmp2)
	toFile('Source;Target',tmp3)

#Funcion que retorna una list con los ids de los followers de un usuario
def followers_id(id):
	followers_list = api.followers_ids(id)
	return followers_list

#Function that captures all the tweets of a user and writes them in a temporary file
def get_all_tweets(screen_name,lim,file):
	#Twitter only allows access to a users most recent 3240 tweets with this method
	alltweets = []	
	
	#save the id of the oldest tweet less one
	date_format = "%m/%d/%Y"
	end_time = datetime.strptime(lim, date_format)
	try:
		new_tweets = api.user_timeline(id = screen_name,count=200)
	#save most recent tweets
		alltweets.extend(new_tweets)
		oldest = alltweets[-1].id - 1
		timed = alltweets[-1].created_at 
		#keep grabbing tweets until there are no tweets left to grab
		
		while (len(new_tweets) > 0) and (timed > end_time):
			try:
			#all subsiquent requests use the max_id param to prevent duplicates
				new_tweets = api.user_timeline(id = screen_name,count=200,max_id=oldest)
			#save most recent tweets
				alltweets.extend(new_tweets)
			#update the id of the oldest tweet less one
				oldest = alltweets[-1].id - 1
				timed = alltweets[-1].created_at 
			except tweepy.RateLimitError:
				print("Paused")
				time.sleep(60 * 15)
				continue

		outtweets = [[tweet.id_str,tweet.created_at, time.mktime(tweet.created_at.timetuple()),tweet.text.encode("utf-8")] for tweet in alltweets]

	except IndexError:
		print("User %s seems to don't have tweets.Skipping..." % screen_name)
		outtweets = []
			

	with open(file, 'wb') as f:
		try:
			for p in outtweets: 
				f.write("{a}:;:{b}:;:{c}:;:{d}\n".format(a=p[0],b=p[1],c=p[2],d=p[3]))
		except IndexError:
			pass

#Function that search the hashtags in the user's tweets
def searchUserHashtag(hashtag, filename,lim,user,dbs):
	trobat = False 
	#save the id of the oldest tweet less one
	date_format = "%m/%d/%Y"
	end_time = time.mktime(datetime.strptime(lim, date_format).timetuple())
	#h="#"+hashtag

	laststamp=1
	lasttext='hola'
	lastid=123
	lastdate=datetime.now()
	f = open(filename, "r")

	for line in f:
		try:
			[tweet_id,date,timestamp,text]=line.split(':;:')
			laststamp=timestamp
			lasttext=text
			lastid=tweet_id
			lastdate=date

			if (multiplematch(hashtag,text)) and (float(timestamp) < float(end_time)): 
				trobat = True
				participated ='yes'

				if searchdb(int(user),dbs):
					updatedb(int(user),line,dbs)
					print('update 1, %s'%user)
				else:
					twe=[line]
					followers = followers_id(user)
  					insertdb(int(user),participated,followers,twe,dbs)
  					print('insert 1, %s'%user)
		except:

			if (multiplematch(hashtag,line)) and (float(timestamp) < float(end_time)): 
				trobat = True
				towrite='%s:;:%s:;:%s:;:%s %s:;:%s'%(lastid,lastdate,laststamp,lasttext.rstrip(),line,user)
				participated ='yes'

				if searchdb(int(user),dbs):
					updatedb(int(user),towrite,dbs)
					print('update 2, %s'%user)
				else:
					twe=[towrite]
					followers = followers_id(user)
  					insertdb(int(user),participated,followers,towrite,dbs)
  					print('insert 2, %s'%user)

			continue
	f.close()

	return trobat


#'Main Start'

j=0

init_files(file_tmp,file_tmp2,file_tmp3)
#In this file will be the list obtained from the users found in the streaming capture 
file_object  = open(file_orig, "r")
#print('%s'%(hasht[0]))
print('Start 1st phase')
#First add the users that we know that participated to the database
for line in file_object:
	user=line.rstrip()
	if (searchdb(int(user),dbi)):
		print("%s has profile in the database. -Phase 1" %user)
	else:
		try:
		
			print("Try to get %s tweets. - Phase 1" % user)
			get_all_tweets(user,date_orig,file_tmp)
		
			searchUserHashtag(hasht,file_tmp,date_fin,user,dbi)
			text="%s;%s"%(j,user)
			toFile(text,file_tmp2)
			j+=1		

		except tweepy.RateLimitError:
			print("Paused - Phase 1")
			time.sleep(60 * 15)
			continue
		except tweepy.TweepError:
	 		print("Failed to run the command on user %s Skipping... - Phase 1" % user)
	 		
file_object.close()

print('Start 2nd phase')

file_object2  = open(file_orig, "r")
#In this part, search for new users that participated from the followers until it cannot find more
for line in file_object2:
 	user=line.rstrip()
 	i=0
 	try:
 		if (searchdb(int(user),dbi)):
 		 	cursor = dbi.find({"_id":int(user)})
 		 	for document in cursor:
 		 		lista = document['followers']
 		 		#print ('Esta, en la lista :%s ' %(user) )
 		else:
 			try:
 		 		lista = followers_id(user)
 		 		#print ('No esta, en la lista :%s ' %(user) )
 		 		text="%s;%s"%(j,lista[i])
 	 			toFile(text,file_tmp2)
 	 			j+=1
 		 	except tweepy.RateLimitError:
 	 			print("Paused - Phase 2 followers")
 	 			time.sleep(60 * 15) 	 			 		 		
 	 			lista = followers_id(user)
		
 		while (i < len(lista)):
 	 		text="%s;%s"%(user,lista[i])
 	 		toFile(text,file_tmp3)
		
 	 		if(searchdb(int(lista[i]), dbi)):
 	 			print("%s has a profile in the database." % (lista[i]))

 	 		else:
 	 			print("%s hasn't a profile in the database." % (lista[i]))
 	 			text="%s;%s"%(j,lista[i])
 	 			toFile(text,file_tmp2)
 	 			j+=1
	 			

 	 			print("Try to get %s tweets." % lista[i])
 	 			try:
 	 				get_all_tweets(lista[i],date_orig,file_tmp)
 	 			except tweepy.RateLimitError:
 	 				print("Paused - Phase 2-tweets")
 	 				time.sleep(60 * 15)
 	 				continue
 	 			if(searchUserHashtag(hasht,file_tmp,date_fin,lista[i],dbi)):#añadir y buscar si es nuevo  un update
 	 				now = time.strftime("%c") 
 	 				toFile(lista[i],file_orig)
 	 				print("User %s participated.%s" % (lista[i],now))
 	 			else:
 	 				now = time.strftime("%c")
 	 				follower_lista = []
 	 				tweets=[]
 	 				insertdb(lista[i],'no',follower_lista,tweets,dbi)#con no participado
 	 				print("User %s not participated.%s" % (lista[i],now))			
  			i+=1

	
 	except tweepy.RateLimitError:
 	 	print("Paused - Phase 2")
 	 	time.sleep(60 * 15)
 	 	continue
 	except tweepy.TweepError:
 	 	print("Failed to run the command on user %s Skipping... - Phase 2" % lista[i])
 	 	i+=1
#Remove temporal files
os.remove(file_tmp)
print 'Finished'
