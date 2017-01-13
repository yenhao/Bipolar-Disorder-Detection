
# coding: utf-8

# python2

from EmotionDetection import EmotionDetection
from collections import defaultdict
import plotly.plotly as py
import plotly.graph_objs as go
import os
import pytz
from datetime import datetime


# ## Read Patients

def readPatient(folder, filename):
    with open(folder + filename, 'r') as openfile:
        return [line.strip().split('\t') for line in openfile.readlines()]

def checkFolderFile(folder):
    return os.listdir(folder)


def readPatientIllTime(folder, filename):
    with open(folder + filename, 'r') as openfile:
        return [line.strip().split('\t') for line in openfile.readlines()]

def readPatientTimezone(folder, filename):
    time_dict = {}
    with open(folder + filename, 'r') as openfile:
        for line in openfile.readlines():
            split = line.strip().split('\t')
            if split[2] != None:
                time_dict[split[1][1:]] = split[2]
            else:
                continue
    return time_dict


print('\n Reading patient tweets..')
folder = '../twitter crawler/patient_tweets_nourl/'
print(folder)
patient_list = checkFolderFile(folder)
patient_tweets_dict = defaultdict(lambda : [])
for patient_name in patient_list:
    patient_tweets_dict[patient_name] = readPatient(folder, patient_name)
    


# ## Get patient timezone
print('\n Getting patient timezone..')
patient_timezone_dict = readPatientTimezone('../twitter crawler/','bipolar_user_timezone')

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
    'Dublin':'Europe/Dublin',
    'Mountain Time (US & Canada)':'Mountain/US',
    'Hawaii':'Pacific/Honolulu',
    'Brisbane':'Australia/Brisbane',
    'Vienna':'Europe/Vienna',
    'Islamabad':'Asia/Karachi',
    'Casablanca':'Africa/Casablanca',
    'Yakutsk':'Asia/Yakutsk',
    'Tijuana':'America/Tijuana',
    'Africa/Johannesburg':'Africa/Johannesburg',
    'Mountain Time (US & Canada)':'US/Central'
}


def to_local_timezone(local, orig_time):
    dt = datetime.strptime(orig_time, "%Y-%m-%d %H:%M:%S")
    dt = pytz.timezone(local).localize(dt)
    est_dt = dt.astimezone(pytz.timezone('EST'))

    return est_dt.strftime("%Y-%m-%d %H:%M:%S")


# ## Get ill time information
print('\n Getting ill time..')
patient_ill_time_list = readPatientIllTime('../twitter crawler/', 'bipolar_list')
patient_ill_time_dict = {line[0]: line[1] for line in patient_ill_time_list}

patient_month_time_dict = {}
patient_year_time_dict ={}

for patient in patient_ill_time_dict:
    if len(patient_ill_time_dict[patient].split('/')) > 1:
        patient_month_time_dict[patient] = patient_ill_time_dict[patient]
    else:
        continue

# # Analyse the post frequence
# ## By Day
print('\n Creating daily dictionary..')
# patient_name -> date time -> tweets_time<\t>tweet
patient_day_tweets = defaultdict(lambda: defaultdict(lambda: []))
for patient in patient_tweets_dict:
    try:
        local = timezone_location_dict[patient_timezone_dict[patient]]
    except:
        continue
        
    for tweet in patient_tweets_dict[patient]:
        local_time = to_local_timezone(local,tweet[2])
        date, time = local_time.split(' ')
        date = int(date.replace('-',''))  
        try:
            patient_day_tweets[patient][date].append(local_time + '\t' +tweet[3])
        except:
            patient_day_tweets[patient][date].append(local_time + '\t<empty_tweets>')
    

print('\n Release patient tweets dictionary') 
patient_tweets_dict = None

# ## Chart
import numpy as np

ed = EmotionDetection()

folder = 'patient emotion/'

print('\n Start to go through patients')

# ## Late + Frequence
for patient in patient_day_tweets:
    print('\t'+patient)
    outfile = open(folder + patient,'w')

    lx_axis = []
    ly_axis = []
    y = []
    try:
        ill_time = patient_month_time_dict[patient]
    except:
        print('\t No ill time')
        continue

    # Calculate illness start and end
    ill_time_list = ill_time.split('/')
    
    lyear = int(ill_time_list[0])
    lmonth = int(ill_time_list[1])
    try:
        lday = int(ill_time_list[2])
    except: 
        lday = 1
    
    end_month = lmonth+3
    start = datetime(lyear-1,lmonth,lday)
    if end_month > 12:
        end = datetime(lyear+1,end_month-12,lday)
    else:
        end = datetime(lyear,end_month,lday)
    # Enc calculation

    print('\n Start to query emotion!')
    sorted_date_patient = sorted(patient_day_tweets[patient])
    for date in sorted_date_patient:
        date = str(date)
        format_datetime = datetime(int(date[:4]),int(date[4:6]),int(date[6:]))

        # print(str(start)+'\t'+str(format_datetime) + '\t' + str(end))
        if( start <= format_datetime and format_datetime <= end):

            tweets_list = patient_day_tweets[patient][int(date)]
            print(len(tweets_list))
            for tweet in tweets_list:
                try:
                    tweet = tweet.split('\t')[1]
                    emotion_json = ed.get_emotion_json(tweet)
                    # patient<\t>date<\t>tweet<\t>emotion1<\t>emotion2<\t>ambiguous
                    out_format = '{}\t{}\t{}\t{}\t{}\t{}\n'.format(patient, date, tweet, emotion_json[u'groups'][0][u'name'], emotion_json[u'groups'][1][u'name'], emotion_json[u'ambiguous'])
                    print(out_format)
                    outfile.write(out_format)
                except:
                    continue

    outfile.close()

