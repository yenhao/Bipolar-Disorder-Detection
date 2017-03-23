from flask import Flask, render_template, url_for, request
from collections import defaultdict
import random
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
import pytz

app = Flask(__name__)

# function to delete url
def del_url(line):
    return re.sub(r'(\S*\.com\S*)|(https?:\/\/\S*)', "", line)
# replace hashtag
def checktag(line): 
    return re.sub(r'\@\S*', " <username> ", line)

user_info_dict = defaultdict(lambda: None)
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
    'Fiji': 'Pacific/Fiji'
}

def to_local_timezone(local, orig_time):
    dt = datetime.strptime(orig_time, "%Y-%m-%d %H:%M:%S")
    dt = pytz.timezone(local).localize(dt)
    est_dt = dt.astimezone(pytz.timezone('EST'))
    return est_dt

def readTimezone(folder, filename):
    time_dict = {}
    with open(folder + filename, 'r') as openfile:
        for line in openfile.readlines():
            split = line.strip().split('\t')
            if split[2] != 'None':
                time_dict[split[0]] = split[2]
            else:
                continue
    return time_dict

def getUsersTweets(dbName,collectionName, en_threshold=0.9, timezone_dict = timezone_location_dict ,regular_timezone_dict = readTimezone('../../../twitter crawler/','regularUser_en_fixed_timezone')):
    cursor = MongoClient("localhost", 27017)[dbName][collectionName].find()
    # lang_ratios = getLangRatio(cursor)
    cursor = MongoClient("localhost", 27017)[dbName][collectionName].find()
    usersTweets = {}
    for tweet in cursor:
        userID = tweet["user"]["id"]
        
        try:
            user_timezone = timezone_dict[regular_timezone_dict[str(userID)]]
        except:
            continue
            
        # if lang_ratios[userID] < en_threshold: continue
        #Processing emotions from Carlos' API
        emotion =  tweet["emotion"]["groups"][0]["name"]
        if len(tweet["emotion"]["groups"]) > 1:
            emotion_2 = tweet["emotion"]["groups"][1]["name"]
            
        ambiguous = True if tweet['emotion']['ambiguous'] == 'yes' else False
       
        if len(tweet["emotion"]["groups"]) > 1:
            emotion_2 = tweet["emotion"]["groups"][1]["name"]    
        else:
            emotion_2 = None
        if tweet["polarity"] == "positive":
            polarity = 1
        elif tweet["polarity"] == "negative":
            polarity = -1
        else:
            polarity = 0

        date = to_local_timezone( user_timezone, tweet["created_at"].strftime("%Y-%m-%d %H:%M:%S")) - timedelta(hours = 8) #Modify the time! Because get all tweets is from taiwan(+8) not +0
        text = tweet['text']

        if userID not in usersTweets:
            usersTweets[userID] = {}
        if date not in usersTweets[userID]:
            usersTweets[userID][date] = {}
            
        usersTweets[userID][date]['text'] = text
        usersTweets[userID][date]['name'] = userID
        usersTweets[userID][date]['polarity'] =  polarity
        usersTweets[userID][date]['emotion'] =  emotion
        usersTweets[userID][date]['emotion_2'] =  emotion_2
        usersTweets[userID][date]['ambiguous'] =  ambiguous


    for user in usersTweets:
        sorted_usersTweets = sorted(usersTweets[user])
        global user_info_dict
        user_info_dict[str(userID)] = ('20150101', sorted_usersTweets[0].strftime("%Y%m%d"), sorted_usersTweets[-1].strftime("%Y%m%d"), 'I am Regular User!')

    return usersTweets

def getTweetLFCount(user):
    print('Get Tweet Freq Late Count! \n')
    date_list = []
    post_list = []
    late_list = []
    sorted_date_user = sorted(regular_tweets[user])
    last_date = None
    for date in sorted_date_user:
        # Check date change
        if last_date != None:
            date_diff = (date - last_date).days
            # If day difference > 1day
            # Append the gap, with date, frequence = 0, late = 0
            if date_diff > 1:
                for i in range(date_diff)[1:]:
                    temp_date = convertDatetime(last_date) + timedelta(days=i)
                    temp_date = temp_date.strftime("%Y%m%d")
                    date_list.append(str(temp_date)[:4]+'-'+str(temp_date)[4:6]+'-'+str(temp_date)[6:])
                    post_list.append(0)
                    late_list.append(0)
        
        last_date = date
        temp_date = date.strftime("%Y%m%d")
        date_list.append(str(temp_date)[:4]+'-'+str(temp_date)[4:6]+'-'+str(temp_date)[6:])
        post_count = len(user_tweets_dict[user][date])
        post_list.append(post_count)

        late_count = 0
        # datetime, content, sentiment, emotion1, emotion2, ambiguous
        
        if int(date.hour) < 6:
            late_count +=1
        late_list.append(late_count)
    return (zip(date_list, post_list), zip(date_list, late_list), date_list[0], date_list[1] ,len(date_list))

@app.route("/index")
def index2():
    index = request.args.get('user')
    if index:
        index = int(index)
    else:
        index = 1
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    tweets_list = []

    return render_template("index2.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)

@app.route("/queryname")
def queryname():
    username = request.args.get('user')

    if username in user_list:
        index = user_list.index(username)
    else:
        print("No User")
        index = 1
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    tweets_list = []
    # {username:{(illtime,start,end,statement)}}
    
    return render_template("index2.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)


@app.route("/view2", methods=['GET'])
def view2():
    index = int(request.args.get('user'))
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    return render_template("index2.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)

@app.route("/previous2", methods=['GET'])
def previous2():
    index = int(request.args.get('user')) -1
    if index < 0 :
        index = len(user_list)-1
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    return render_template("index2.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)

@app.route("/next2", methods=['GET'])
def next2():
    index = int(request.args.get('user')) +1
    if index == len(user_list):
        index = 0
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    return render_template("index2.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)


@app.route("/getTweets", methods=['POST'])
def returnTweets():
    user = request.form['user']
    start = request.form['start']
    end = request.form['end']

    print('Query getTweets : User : ' + user + ', Start from ' + start + ', End at ' + end)
    #Generate user tweets html
    html_content = '''
        <div class="row">
            <h3>Tweets from {} to {} </h3>
        </div>
        <br/>
        <div class="list-group" style="padding-bottom:150px">
        '''.format(start, end)
    tweets_text = ''
    sorted_date_user = sorted(user_tweets_dict[user])
    # datetime, content, sentiment, emotion1, emotion2, ambiguous
    for date in sorted_date_user:
        if date >= int(start.replace('/','')) and date <= int(end.replace('/','')):
            tweets = user_tweets_dict[user][date]
            for tweet in tweets:
                html_content += '''
                    <a class="list-group-item">
                        <h4 class="list-group-item-heading">{}</h4>
                        <p class="list-group-item-text">{}</p>
                    </a>
                    '''.format(tweet[1],tweet[0])
                tweets_text += checktag(del_url(tweet[1])) + ' '
    html_content += '</div><center><a class="btn btn-lg btn-default" href="#head" role="button">Top</a></center><br/>'


    filename = user + '_' +start.replace('/','') + end.replace('/','') + '.png'
    # if exist means duplicate
    if os.path.exists('static/img/wordcloud/' + filename): 
        print('Duplicate File! ' + filename)
    else:
        # Generate a word cloud image
        # lower max_font_size
        wordcloud = WordCloud(max_font_size=60, scale=2).generate(tweets_text)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis("off")
        # plt.show()
        fig = plt.gcf()
        # fig.set_size_inches(18.5, 14.5, forward=True)
        
        fig.savefig('static/img/wordcloud/' + filename, dpi=250)
        plt.clf()

    img_html = "<img src=\"/static/img/wordcloud/"+filename+"\" >"

    return str(img_html) + '!@!@!' + str(html_content)

@app.route("/viewTweets")
def viewTweets():
    index = int(request.args.get('index'))
    user = request.args.get('user')
    start = request.args.get('start')
    end = request.args.get('end')

    
    print('Query getTweets : User : ' + user + ', Start from ' + start + ', End at ' + end)
    print('Index : ' + str(index))

    #Generate user tweets html
    html_content = '''
        <div class="row">
            <h3>Tweets from {} to {} </h3>
        </div>
        <br/>
        <div class="list-group" style="padding-bottom:150px">
        '''.format(start, end)
    tweets_text = ''
    # Prepare tweets list
    sorted_date_user = sorted(user_tweets_dict[user])
    # datetime, content, sentiment, emotion1, emotion2, ambiguous
    tweets_list = []
    for date in sorted_date_user:
        if date >= int(start.replace('/','')) and date <= int(end.replace('/','')):
            tweets = user_tweets_dict[user][date]
            for tweet in tweets:
                html_content += '''
                    <a class="list-group-item">
                        <h4 class="list-group-item-heading">{}</h4>
                        <p class="list-group-item-text">{}</p>
                    </a>
                    '''.format(tweet[1],tweet[0])
                tweets_text += checktag(del_url(tweet[1])) + ' '
                # Append tweets list
                tweets_list.append(tweet[0] + '|~|~|' + tweet[1].decode('utf-8').replace('\\','\\\\') + '|~|~|' + tweet[2].strip())
    html_content += '</div><center><a class="btn btn-lg btn-default" href="#head" role="button">Top</a></center><br/>'


    filename = user + '_' +start.replace('/','') + end.replace('/','') + '.png'
    # if exist means duplicate
    if os.path.exists('static/img/wordcloud/' + filename): 
        print('Duplicate File! ' + filename)
    else:
        # Generate a word cloud image
        # lower max_font_size
        wordcloud = WordCloud(max_font_size=60, scale=2).generate(tweets_text)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis("off")
        # plt.show()
        fig = plt.gcf()
        # fig.set_size_inches(18.5, 14.5, forward=True)
        
        fig.savefig('static/img/wordcloud/' + filename, dpi=250)
        plt.clf()

    img_url = "/static/img/wordcloud/"+filename

    # Finish generate html content and wordcloud

    return render_template("emotion_tweets.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], htmlTweets = str(html_content).decode('utf-8'), img_url = img_url, tweets_list = tweets_list, index=index)



print('Load tweets from Mongodb')
regular_tweets =  getUsersTweets("eric","regularUser_en_fixed_emotion")

if __name__ == '__main__':

    app.run('0.0.0.0',debug = False)