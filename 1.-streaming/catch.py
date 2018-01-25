import tweepy
from tweepy import OAuthHandler

consumer_key = '--- Your KEY---'
consumer_secret = '--- Your KEY---'
access_token = '--- Your KEY---'
access_secret = '--- Your KEY---'

name = 'cat'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

from tweepy import Stream
from tweepy.streaming import StreamListener
 
class MyListener(StreamListener):
    #Print input data
    def on_data(self, data):
        try:
            with open(name+'.txt', 'a') as f:
                f.write(data)
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True
 
    def on_error(self, status):
        print(status)
        return True

#'Start main'
 twitter_stream = Stream(auth, MyListener())
twitter_stream.filter(track=[name])