#author: Hao

#Import the file 'ts_R_csv.csv' as data.frame object
#Change the path
library(readr)
ts_R_csv <- read_csv("~/Desktop/ts_R_csv.csv", col_names = FALSE)

#Sorted vector with all the timestamps of the tweets 
tweets_timestamp<-sort(as.vector(ts_R_csv$X1),decreasing = F)

#the number of breaks must be changed for the number or T desired
#histogram of the tweets
hist(tweets_timestamp,breaks=10000)
