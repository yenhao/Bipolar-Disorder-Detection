from flask import Flask, render_template, url_for, request
from collections import defaultdict
import random
from os import path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

app = Flask(__name__)

# function to delete url
def del_url(line):
    return re.sub(r'https?:\/\/.*', "", line)

# Initial
def loadTweets():
    print('Loading Daily Tweets..')
    # {username:{int(date):{[(datetime,content),...]}}}
    tweets_dict = defaultdict(lambda: defaultdict(lambda:[]))
    with open('../../organized/date_tweets') as tweets:
        for line in tweets.readlines():
            username, date, datetime, content = line.split('\t')
            tweets_dict[username][int(date)].append((datetime, content))

    global user_tweets_dict
    user_tweets_dict = tweets_dict
    print('Finished! \n')

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

    global user_info_dict
    user_info_dict = user_dict
    print('Finished! \n')

def init():
    loadTweets()
    loadUserInfo()

user_tweets_dict = None
user_info_dict = None


init()

print('User Count for user_tweets is %d' % len(user_tweets_dict))
print('User Count for user_info is %d' % len(user_info_dict))

user_list = [user for user in user_info_dict]
print('User list has been built!')


@app.route("/")
def index():
    index = random.randrange(0, len(user_list)-1)
    return render_template("index.html", user = str(user_list[index]), user_info_dict = user_info_dict[str(user_list[index])], user_tweets_dict = user_tweets_dict[str(user_list[index])])

@app.route("/pevious")
def previous():
    user = request.form['user']
    index = user_list.index(user)
    return render_template("index.html", user = str(user_list[index]), user_info_dict = user_info_dict[str(user_list[index])], user_tweets_dict = user_tweets_dict[str(user_list[index])])

@app.route("/getTweets", methods=['POST'])
def returnTweets():
    user = request.form['user']
    start = request.form['start']
    end = request.form['end']

    #Generate user tweets html
    html_content = '''
        <div class="row">
            <h3>Tweets from {} to {} </h3>
        </div>
        <br/>
        <div class="list-group" style="padding-bottom:150px">
        '''.format(start, end)
    tweets_text = ''
    for date in user_tweets_dict[user]:
        if date >= int(start.replace('/','')) and date <= int(end.replace('/','')):
            tweets = user_tweets_dict[user][date]
            for tweet in tweets:
                html_content += '''
                    <a class="list-group-item">
                        <h4 class="list-group-item-heading">{}</h4>
                        <p class="list-group-item-text">{}</p>
                    </a>
                    '''.format(tweet[1],tweet[0])
                tweets_text += del_url(tweet[1]) + ' '
    html_content += '</div><center><a class="btn btn-lg btn-default" href="#head" role="button">Top</a></center><br/>'



    # Generate a word cloud image
    # wordcloud = WordCloud().generate(tweets_text)

    # plt.imshow(wordcloud)
    # plt.axis("off")

    # lower max_font_size
    wordcloud = WordCloud(max_font_size=40).generate(tweets_text)
    plt.figure()
    plt.imshow(wordcloud)
    plt.axis("off")
    # plt.show()
    fig = plt.gcf()
    # fig.set_size_inches(18.5, 14.5, forward=True)
    filename = user + '_' +start.replace('/','') + end.replace('/','') + '.png'
    fig.savefig('static/img/wordcloud/' + filename, dpi=250)
    plt.clf()

    img_html = "<img src=\"/static/img/wordcloud/"+filename+"\" >"

    return str(img_html) + '!@!@!' + str(html_content)




if __name__ == '__main__':

    if len(user_tweets_dict) == len(user_info_dict) : 
        print('SUCCESS : User Count Match!\n Service Start!')
        app.run(debug = True)
    else:
        print('FAIL : Count doesn\'t Match!\n Shut Down..')


    