from flask import Flask, render_template, url_for, request
from collections import defaultdict
import random
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os
from datetime import datetime, timedelta
from pymongo import MongoClient

app = Flask(__name__)

# function to delete url
def del_url(line):
    return re.sub(r'(\S*\.com\S*)|(https?:\/\/\S*)', "", line)
# replace hashtag
def checktag(line): 
    return re.sub(r'\@\S*', " <username> ", line)

def checkFolderFile(folder):
    return os.listdir(folder)

# Initial
# ## Read BD_user
def loadTweets(folder):
    tweets_dict = defaultdict(lambda:defaultdict(lambda: []))
    for filename in checkFolderFile(folder):
        with open(folder + filename, 'r') as openfile:
            for line in openfile.readlines():
                try:
                    username, date, datetime, content, sentiment, emotion1, emotion2, ambiguous = line.split('\t')
                except:
                    print(line.split('\t'))
                tweets_dict[username][int(date)].append((datetime, content, sentiment, emotion1, emotion2, ambiguous.strip()))
    return tweets_dict

def loadUserInfo():
    print('Loading User Information..')
    statement_dict = {}
    with open('../../../twitter crawler/diagnosed_users_in_bipolar.csv') as statements:
        # username, date, statement
        for line in statements.readlines():
            username = line.split(';')[0]
            date = line.split(';')[1]
            statement_dict[username] = (date, line.split(';')[4])

    # {username:{(illtime,start,end,statement)}}
    user_dict = {}
    with open('../../organized/user_info') as info:
        for line in info.readlines():
            username, illtime, start, end = line.split('\t')
            try:
                statement = statement_dict[username]
            except:
                statement = 'Unavailable'
            user_dict[username] = ((illtime, start, end.strip(), statement))

    return user_dict

user_tweets_dict = loadTweets('../../patient emo_senti/')
user_info_dict = loadUserInfo()

def convertDatetime(orig_time):
    return datetime.strptime(str(orig_time), "%Y%m%d")

def getTweetLFCount(user):
    print('Get Tweet Freq Late Count! \n')
    date_list = []
    post_list = []
    late_list = []
    sorted_date_user = sorted(user_tweets_dict[user])
    last_date = None
    for date in sorted_date_user:
        # Check date change
        if last_date != None:
            date_diff = (convertDatetime(date) - convertDatetime(last_date)).days
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


        date_list.append(str(date)[:4]+'-'+str(date)[4:6]+'-'+str(date)[6:])
        post_count = len(user_tweets_dict[user][date])
        post_list.append(post_count)

        late_count = 0
        # datetime, content, sentiment, emotion1, emotion2, ambiguous
        for tweet in user_tweets_dict[user][date]:
            tweet_time = tweet[0]
            if int(tweet_time.split(' ')[1].split(':')[1]) < 6:
                late_count +=1
        late_list.append(late_count)
    return (zip(date_list, post_list), zip(date_list, late_list), date_list[0], date_list[1] ,len(date_list))




@app.route("/")
def index():
    index = 1
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    tweets_list = []
    return render_template("index.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)

@app.route("/view", methods=['GET'])
def view():
    index = int(request.args.get('user'))
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    return render_template("index.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)

@app.route("/previous", methods=['GET'])
def previous():
    index = int(request.args.get('user')) -1
    if index < 0 :
        index = len(user_list)-1
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    return render_template("index.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)

@app.route("/next", methods=['GET'])
def next():
    index = int(request.args.get('user')) +1
    if index == len(user_list):
        index = 0
    print('\n\nRetrieving User : ' + str(user_list[index]).decode('utf-8'))
    print('Index : ' + str(index))
    return render_template("index.html", user = str(user_list[index]).decode('utf-8'), user_info_dict = user_info_dict[str(user_list[index])], LFlist = getTweetLFCount(str(user_list[index])), index=index)
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


print('User Count for user_tweets is %d' % len(user_tweets_dict))
print('User Count for user_info is %d' % len(user_info_dict))

user_list = [user for user in user_info_dict]
print('User list has been built!')



if __name__ == '__main__':

    # if len(user_tweets_dict) == len(user_info_dict) : 
    #     print('SUCCESS : User Count Match!\n Service Start!\n\n')
    #     app.run('0.0.0.0',debug = False)
    #     # app.run()
    # else:
    #     print('FAIL : Count doesn\'t Match!\n Shut Down..\n\n')
    app.run('0.0.0.0',debug = False)