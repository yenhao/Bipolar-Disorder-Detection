# this code is from jamie
from time import time
from time import sleep
from twython import Twython
from twython import TwythonAuthError
from twython import TwythonRateLimitError
from twython import TwythonError
from warnings import warn
from datetime import datetime
import math
# from pymongo import MongoClient
import csv

# import config
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
 

def getTweets(screen_name=None, user_id=None, num=0, include_rts=False):
    twitter = Twython(consumer_key, consumer_secret,access_token,access_token_secret )

    tweets = None
    while(tweets == None):
        try:
            if screen_name == None:
                tweets = twitter.get_user_timeline( user_id = user_id, count = 200, trim_user = 1, include_rts = include_rts )
            else:
                tweets = twitter.get_user_timeline( screen_name = screen_name, count = 200, trim_user = 1, include_rts = include_rts )
        except TwythonRateLimitError:
            remainder = math.fabs(math.ceil(float(twitter.get_lastfunction_header(header='x-rate-limit-reset')) - time()))
            print("Waiting for {} secs...".format(remainder))
            sleep(remainder)
            print("tweets Reconnecting...")
            continue
        except  TwythonAuthError:
            print ("tweets Bad Authentication")
            return []
        except TwythonError:
            print ("tweets 404 not found")
            continue
            # return []


    totalTweets = tweets
    while len(tweets) >= 2:
        max_id = tweets[-1]["id"]
        try:
            if screen_name == None:
                tweets = twitter.get_user_timeline(user_id = user_id, max_id = max_id, count = 200, trim_user = 1, include_rts = include_rts )
            else:
                tweets = twitter.get_user_timeline(screen_name = screen_name, max_id = max_id, count = 200, trim_user = 1, include_rts = include_rts )

        except TwythonRateLimitError:
            remainder = math.fabs(math.ceil(float(twitter.get_lastfunction_header(header='x-rate-limit-reset')) - time()))
            print("Waiting for {} secs...".format(remainder))
            sleep(remainder)
            print("tweets Reconnecting...")
            continue
        except TwythonError:
            print('tweets twythonerror')
            # return[]
            continue

        if len(tweets) > 1:
            totalTweets += tweets[1:]
        elif num > 0 and len(tweets) >= num:
            break


    for i in range(len(totalTweets)):
        date = totalTweets[i]["created_at"]
        totalTweets[i]["created_at"] = datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')

    if num == 0:    # 'num' is used to decide getting all tweets or latest limited tweets
        return totalTweets
    else:
        return totalTweets[:num]

def getFollowers(screen_name):
    twitter = Twython( consumer_key, consumer_secret,access_token,access_token_secret )

    while(True):
        try:
            followers = twitter.get_followers_ids(screen_name=screen_name)
            followers_id = followers['ids']
            return followers_id
        except TwythonRateLimitError:
            print ("follower Fall asleep")
            sleep(360) # unit:sec
            print ("follower Wake up")
            pass
        except TwythonError:
            print ("follower 404 not found")
            # return []
            pass
        except TwythonAuthError:
            print ("follower Bad Authentication")
            # return []
            pass

def getUserProfile(screen_name=None, user_id=None):
    twitter = Twython( consumer_key, consumer_secret,access_token,access_token_secret )

    while(True):
        try:
            if screen_name == None:
                user_profile = twitter.show_user(id=user_id)
            else:
                user_profile = twitter.show_user(screen_name=screen_name)
            return user_profile
        except TwythonRateLimitError:
            remainder = math.fabs(math.ceil(float(twitter.get_lastfunction_header(header='x-rate-limit-reset')) - time()))
            print("Waiting for {} secs...".format(remainder))
            sleep(remainder)
            print("Reconnecting...")
            continue
        except TwythonAuthError:
            print ("Bad Authentication")
            return []
        except TwythonError:
            print ("404 not found")
            return []

def removelinechange(sentence):
    result = sentence.replace('\n',' ')
    result = result.replace('\r', ' ')
    return result

if __name__ == '__main__':

    keyword_list = [YOUR KEYWORD LIST]
    portal_list = [YOUR PORTAL LIST]

    for portal in portal_list[7:]:
        portal_file = open('portal/'+ portal + "_user_profile","a")
        followes_list = getFollowers('@'+portal)
        print (portal + '\t' + str(len(followes_list)))#4329/5000

        for each_follower in followes_list:
            user_profile = getUserProfile(user_id = each_follower)
            try:
                if user_profile['lang'] != 'en':continue
            except:
                print('***********************************')
                print('Lang selection error')
                print('***********************************\n')
                continue
            if len(user_profile) != 0:
                # for keywrod in keyword_list:
                #     if keywrod in user_profile['description']:
                try:
                    out_content = "{}\t@{}\t{}\t{}\n".format(user_profile['id_str'], user_profile['screen_name'], user_profile['created_at'], removelinechange(user_profile['description']))
                    print (out_content)
                    portal_file.write(out_content)
                    # break
                except:
                    print('***********************************')
                    print(user_profile['id_str'] + '  Encoding error..')
                    print('***********************************\n')
                    
            # data = []
            # if len(getTweets(user_id = each_follower)) != 0:
                # data = getTweets(user_id = each_follower)
                # print data
                # if getTweets(user_id = each_follower) != []:
                # if getTweets(user_id = each_follower) != []:
        #             # insert_cursor.insert_many(getTweets(user_id = each_follower))#insert into mongoDB
        #         #print data
        #     print (each_follower)

        portal_file.close()