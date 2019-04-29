import sys,os
sys.path.append('GetOldTweets-python/') # get old tweets library
import got
import tweepy
import time
import better_exceptions
from datetime import datetime, timedelta

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

count_num = 0

def getUsername(api, userid):
    user = api.get_user(userid) 
    return user.screen_name


def getEachTweet(userID , username, tweet):
    out_format = "{}\t{}\t{}\t{}\n".format(userID, username, str(tweet.date), str(tweet.text.encode('utf-8')))
    return(out_format)
    # possible entry
    # tweet.id
    # tweet.permalink
    # tweet.username
    # tweet.text
    # tweet.date
    # tweet.retweets
    # tweet.favorites
    # tweet.mentions
    # tweet.hashtags
    # tweet.geo

def getUserIdList():
    with open('mention_recent_bipolar') as open_file:
        return [(line.split('\t')[0],line.split('\t')[-1]) for line in open_file.readlines()]

def timeout(STime):
    print('Sleep for ' + str(STime) + ' seconds..')
    print('\n\n')
    time.sleep(STime)
    

def main():
    # Twitter api setup
    # To query the user screen name
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    user_list = getUserIdList()
    # user_list = ['itsmovies','SportsCenter','BBCSport']
    for id_num_tuple in user_list:
        global count_num
        count_num = 0
        userID = id_num_tuple[0]
        recent_time = id_num_tuple[1].strip()
        recent_dt = datetime.strptime( recent_time , "%Y/%m/%d")
    
        try:
            username = getUsername(api,userID)
            # username = id_num_tuple[0]

            print(str(user_list.index(id_num_tuple)+1) + '\t' + username + '\t' + id_num_tuple[1])
        except:
            print('UserID ' + userID + ' is not found on Twitter..')
            continue
        print(str(datetime.now())[:-7])
        print('Crawling every tweets of ' + username + ' ..')

        out_folder = 'mention_recent'
        def tweetsToFile(tweets):
            # make sure have output folder
            if not os.path.exists(out_folder):
                os.makedirs(out_folder)
            output_content = ''
            with open(out_folder + '/' + userID,'a') as output_file:
                for tweet in tweets:
                    output_content += getEachTweet(userID, username, tweet)
                output_file.write(output_content)

            global count_num
            count_num += len(tweets)
            print( str(datetime.now())[:-7] +' - Total ' + str(count_num) + ' tweets in ' + out_folder + '/' +userID)            

        # if exist means duplicate
        if os.path.exists( out_folder + '/' + userID): 
            print('Duplicate user! ' + userID)
            continue

        from_time = (recent_dt - timedelta(weeks = 27)).strftime("%Y-%m-%d")
        to_time = (recent_dt + timedelta(weeks = 2)).strftime("%Y-%m-%d")
        print('Start to crawl from {} to {}'.format(from_time, to_time))
        tweetCriteria = got.manager.TweetCriteria().setUsername(username).setSince(from_time).setUntil(to_time)
        got.manager.TweetManager.getTweets(tweetCriteria, tweetsToFile, 100)
        print('\n\n')
        timeout(count_num/60)
        

if __name__ == '__main__':

    main()
