import sys,os
# get old tweets lib
sys.path.append('GetOldTweets-python/')
import got
import tweepy
import time
from datetime import datetime

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

count_num = 0

def getUsername(api, userid):
    user = api.get_user(userid) 
    return user.screen_name


def getEachTweet(userID, username, tweet):
    out_format = "{}\t{}\t{}\t{}\n".format(userID, username, str(tweet.date), str(tweet.text.encode('utf-8')))
    return(out_format)
    # Possible entry
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
    # Target_ID <tab> TARGET_ORIGINAL_TWEETS_COUNT  
    with open(YOUR TARGET FILE) as open_file:
        return [(line.split('\t')[0],line.split('\t')[1]) for line in open_file.readlines()]

    def timeout(STime):
    print('Sleep for' + str(STime) + 'seconds..')
    time.sleep(STime)
    print('\n\n')

def main():
    #twitter api setup
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    user_list = getUserIdList()
    # Check every user in your list
    for id_num_tuple in user_list:
        global count_num
        count_num = 0
        userID = id_num_tuple[0]
        try:
            username = getUsername(api,userID)
            print(str(user_list.index(id_num_tuple)+1) + '\t' + username + '\t' + id_num_tuple[1])
        except:
            print('UserID ' + userID + ' is not found on Twitter..')
            continue
#         To show the process start time    
        print(str(datetime.now())[:-7])
        print('Crawling every tweets of ' + username + ' ..')
        
        # To detect if the file has been collect before
        # If repeat, continue to next one
        out_folder = 'YOUR OUTPUT FOLDER'
        if os.path.exists(out_folder + '/' + userID):
            print('Duplicate user: ' + userID +'\n')
            continue
            
        # Method to handle the tweet buffer
        # From got.manager.TweetManager.getTweets(tweetCriteria, tweetsToFile, 100)
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
            
            # Show how many tweets you have collected, also show the time (You can check the time to decide restart time)
            print('{}\tTotal {} tweets in {}/{}'.format(str(datetime.now())[:-7], str(count_num), out_folder, userID))
            

        tweetCriteria = got.manager.TweetCriteria().setUsername(username).setUntil(YOUR ENDING DATE)
        got.manager.TweetManager.getTweets(tweetCriteria, tweetsToFile, 100)
        print('\n\n')
        # Time out to prevend IP ban
        timeout(count_num/60)

        

if __name__ == '__main__':

    main()
    
