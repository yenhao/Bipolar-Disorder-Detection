from flask import Flask, render_template, url_for
from collections import defaultdict
import random

app = Flask(__name__)

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

@app.route("/initusr")
def firstusr():
    return render_template('result.html', result = dict)




if __name__ == '__main__':

    if len(user_tweets_dict) == len(user_info_dict) : 
        print('SUCCESS : User Count Match!\n Service Start!')
        app.run(debug = True)
    else:
        print('FAIL : Count doesn\'t Match!\n Shut Down..')


    