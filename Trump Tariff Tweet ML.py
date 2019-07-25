#!/usr/bin/env python
# coding: utf-8

# In[1]:


#importing all the relevant modules needed for this project

import pandas as pd
import numpy as np
import tweepy as tw
import json
import sys
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from numpy import array
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json

#importing all the relevant modules needed for this project

#setting the max iteration for our Logistic Regression function

logClassifier = LogisticRegression(max_iter=100)

plt.style.use('classic')
get_ipython().run_line_magic('matplotlib', 'inline')


CONSUMER_KEY    = ''
CONSUMER_SECRET = ''

# Access:
ACCESS_TOKEN  = ''
ACCESS_SECRET = ''

def twitter_setup():
    """
    Utility function to setup the Twitter's API
    with our access keys provided.
    """
    # Authentication and access using keys:
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    # Return API with authentication:
    api = tweepy.API(auth)
    return api

extractor = twitter_setup()

tweets = extractor.user_timeline(screen_name="realDonaldTrump", count=200)


#converting all our Twitter data into a pandas dataframe

data = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])

#ensuring that the dataframe shows all relevant columns and its appropriate values

data['len']  = np.array([len(tweet.text) for tweet in tweets])
data['ID']   = np.array([tweet.id for tweet in tweets])
data['Date'] = np.array([tweet.created_at for tweet in tweets])
data['Source'] = np.array([tweet.source for tweet in tweets])
data['Likes']  = np.array([tweet.favorite_count for tweet in tweets])
data['RTs']    = np.array([tweet.retweet_count for tweet in tweets])
data['created_at'] = pd.to_datetime(data['created_at'], infer_datetime_format=True)
data['created_at'] = data['created_at'].dt.date

data = data[data.columns[-1:].tolist()+data.columns[:-1].tolist()]
data.rename(columns={"created_at": "Date"}, inplace=True)

#extracting the STI historical prices from a CSV file

sti = pd.read_csv("STI.csv")


# In[2]:


#converting the STI datetime to a standardised date format for analysis using sklearn later

sti['Date'] = pd.to_datetime(sti['Date'], infer_datetime_format=True)
sti['Date'] = sti['Date'].dt.date


# In[3]:





# In[4]:


#renaming the column so it would be ready for merging with the STI data

data.rename(columns={"created_at": "Date"}, inplace=True)


# In[5]:


#merging the data

df = pd.merge(data,sti)


# In[28]:


#creating a Change column to reflect the difference in Close prices between 2 consecutive days

df['Change'] = df.groupby('Date').Close.pct_change()


# In[7]:


#removing all rows where there is exactly 0 change. This indicates that the stock market was closed the day before, and will not be affected by Trump's tweets

Marketclosed = df[df['Change'] == 0 ].index
 
# Delete these row indexes from dataFrame
df.drop(Marketclosed, inplace=True)


# In[8]:


df = df.sort_values(by='Date', ascending=True)


# In[37]:


#preparing the array transformation and removal of the first NaN row (because you can't compare any change on the first row)

x = df['Date']
y = df['Change']
z = df['tariff_impact']


y = y[~np.isnan(y)]
z = z[~np.isnan(z)]

y = array(y).reshape(-1,1)
z = array(z).reshape(-1,1)

q = np.delete(z, 0)


# In[38]:


#preparing the Logistic Regression Machine Learning training model

y_train, y_test, q_train, q_test = train_test_split(y,q,test_size=0.10,random_state=0)
logClassifier.fit(y_train, q_train)


# In[39]:


q_pred = logClassifier.predict(q_test)


# In[42]:


metrics.accuracy_score(q_test,q_pred)


# In[46]:


#setting the classification report.

from sklearn.metrics import classification_report
print(classification_report(q_test, q_pred))
q_pred == q_test


# In[47]:


#setting the confusion matrix

confusion_matrix(q_test,q_pred)


# In[ ]:




