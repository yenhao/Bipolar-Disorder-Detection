# coding: utf-8

import os
import re
import json
import pytz
import urllib2
import numpy as np
import pandas as pd
import better_exceptions
from datetime import datetime, timedelta
from EmotionDetection import EmotionDetection


# ## Read Patients
def readPatient(folder, filename):
    print(folder + filename)
    return pd.read_csv(folder + filename, delimiter = "\t", header = None)

def checkFolderFile(folder):
    return os.listdir(folder)


def readPatientTimezone(folder, filename):
    time_dict = {}
    with open(folder + filename, 'r') as openfile:
        for line in openfile.readlines():
            split = line.strip().split('\t')
            if split[2] != "None":
                time_dict[split[1]] = split[2]
            else: 
                continue
    return time_dict

def to_local_timezone(local, orig_time):
    # -8 is because I collect data from taiwan which is +8 not +8
    utc_time = datetime.strptime(orig_time, "%Y-%m-%d %H:%M:%S")-timedelta(hours = 8)
    tz = pytz.timezone(local)
    return pytz.utc.localize(utc_time, is_dst=None).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")



# ## Set Patient Timezone
timezone_location_dict = {
    'Pacific Time (US & Canada)':'US/Pacific',
    'Central Time (US & Canada)':'US/Central',
    'Eastern Time (US & Canada)':'US/Eastern',
    'London':'Europe/London',
    'Sydney':'Australia/Sydney',
    'Tokyo':'Asia/Tokyo',
    'Africa/Nairobi':'Africa/Nairobi',
    'Arizona':'US/Arizona',
    'Kyiv':'Europe/Simferopol',
    'Europe/London':'Europe/London',
    'Atlantic Time (Canada)':'Atlantic/Canary',
    'Midway Island':'Pacific/Apia',
    'Auckland':'Pacific/Auckland',
    'Amsterdam':'Europe/Amsterdam',
    'Baghdad':'Asia/Riyadh',
    'Riyadh':'Asia/Riyadh',
    'Belgrade':'Europe/Belgrade',
    'Quito':'Pacific/Galapagos',
    'Pretoria':'Africa/Johannesburg',
    'Beijing':'Asia/Shanghai',
    'Hong Kong':'Asia/Shanghai',
    'Dublin':'Europe/Dublin',
    'Mountain Time (US & Canada)':'Mountain/US',
    'Hawaii':'Pacific/Honolulu',
    'Brisbane':'Australia/Brisbane',
    'Vienna':'Europe/Vienna',
    'Islamabad':'Asia/Karachi',
    'Casablanca':'Africa/Casablanca',
    'Yakutsk':'Asia/Yakutsk',
    'Tijuana':'America/Tijuana',
    'Johannesburg':'Africa/Johannesburg',
    'Mountain Time (US & Canada)':'US/Central',
    'Bangkok': 'Asia/Bangkok',
    'Harare': 'Africa/Harare',
    'Chennai': 'Asia/Kolkata',
    'Kolkata': 'Asia/Kolkata',
    'Brussels': 'Europe/Brussels',
    'Melbourne': 'Australia/Melbourne',
    'Alaska': 'US/Alaska',
    'Perth': 'Australia/Perth',
    'Denver':'America/Denver',
    'Los Angeles': 'America/Los_Angeles',
    'indiana': 'US/East-Indiana',
    'Vancouver': 'America/Vancouver',
    'Berlin': 'Europe/Berlin',
    'Kentucky': 'America/Kentucky/Louisville',
    'Copenhagen':'Europe/Copenhagen',
    'Athens': 'Europe/Athens',
    'Edinburgh': 'Etc/Greenwich',
    'Wellington': 'Asia/Anadyr',
    'Santiago': 'US/Pacific',
    'America/New_York': 'US/Eastern',
    'Paris': 'Europe/Paris',
    'Jakarta': 'Asia/Jakarta',
    'New Delhi': 'Asia/Calcutta',
    'Chicago': 'US/Central',
    'America/Chicago': 'US/Central',
    'Fiji': 'Pacific/Fiji',
    'US/Mountain': 'US/Mountain'
}


# ## Prepare File

print('\n Reading patient tweets..')
folder = '../twitter crawler/regularUser_en_fixed/'
print(folder)
user_list = checkFolderFile(folder)
user_tweets_list = []
for name in user_list:
    user_tweets_list.append(readPatient(folder, name))

print(' User Number from tweets folder:' + str(len(user_tweets_list)))

# ## Get patient timezone
print('\n Getting patient timezone..')
patient_timezone_dict = readPatientTimezone('../twitter crawler/','regularUser_en_fixed_timezone')

missing_timezone_user_list = []

for user_tweets in user_tweets_list:
    user_name = user_tweets[1][0]
    user_timezone = patient_timezone_dict.get(user_name)
    if user_timezone:
        try:
            user_tweets[2] = user_tweets[2].map(lambda x: to_local_timezone(timezone_location_dict[user_timezone], x)) 
        except:
            print('Timezone Error')
            missing_timezone_user_list.append(user_name)

    else:
        print(user_name)
        missing_timezone_user_list.append(user_name)

# ## Query Emotion & Sentiment
# function to delete url
def del_url(line):
    return re.sub(r'(\S*(\.com).*)|(https?:\/\/.*)', "", line)
# replace tag
def checktag(line): 
    return re.sub(r'\@|\#', "", line)
# Some special character
def checkSpecial(line):
    return line.replace('♡', 'love ').replace('\"','').replace('“','').replace('”','').replace('…','...')

def sendto140(line):
        query_string = '{"data": ['
        # username, date, datetime, content 
        query_string += '{"text": "' + checkSpecial(checktag(del_url(str(line).strip()))) + '"},'

        query_string = query_string[:-1] + ']}'
        try:
            response = urllib2.urlopen('http://www.sentiment140.com/api/bulkClassifyJson', query_string) # request to server     
            page = response.read() # get the response     
            # print page # print the result     
            query_result = json.loads(page) # parse the result. The result is in JSON format
            return sentiment_dict[int(query_result["data"][0]["polarity"])]
        except:
            print("Fail : "+query_string)
            return sentiment_dict[2]



sentiment_dict = {
                0:-1,
                2: 0,
                4: 1
                }

# Emotion query object
ed = EmotionDetection()


output_folder = 'regular_emo_senti/'


for user_tweets in user_tweets_list:
    user_name = user_tweets[1][0]
    # Check if file dulpicate
    # if exist means duplicate
    if os.path.exists(output_folder + user_name): 
        print('Duplicate! ' + user_name)
        continue

#     Change Index to tweet time
    user_tweets.index = user_tweets.set_index(2).index.astype('datetime64[ns]')
#     Filter the time > 15month
    user_tweets = user_tweets[user_tweets.index >= user_tweets.index[0] - timedelta(weeks = 65)]
    print('\n{} - Query user : {}, Tweets : {}\n'.format( datetime.now().strftime("%Y/%m/%d %H:%M:%S"), user_name, user_tweets.shape[0]))
#     Sentiment Query & Emotion Query
    senti_array, emo1_array, emo2_array, amb_array = [], [], [], []

    for line in user_tweets[3]:
        senti_array.append(sendto140(line))

        emotion_json = ed.get_emotion_json(line)
        emotion1, ambiguous = emotion_json[u'groups'][0][u'name'], emotion_json[u'ambiguous']

        if len(emotion_json[u'groups']) == 2:
            emotion2 = emotion_json[u'groups'][1][u'name']
        else:
            emotion2 = emotion1
        emo1_array.append(emotion1)
        emo2_array.append(emotion2)
        amb_array.append(ambiguous)

    senti_array, emo1_array, emo2_array, amb_array = np.array(senti_array), np.array(emo1_array), np.array(emo2_array), np.array(amb_array)

    user_tweets[4] = np.array(senti_array)
    user_tweets[5] = np.array(emo1_array)
    user_tweets[6] = np.array(emo2_array)
    user_tweets[7] = np.array(amb_array)
    
          
    user_tweets.to_csv( output_folder + user_name, header = None, sep = '\t')


print('Done!')
print('These users are missing timezone')
print(missing_timezone_user_list)