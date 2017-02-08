# encoding: utf-8
import urllib2
import json
from collections import defaultdict
import time
import re

# function to delete url
def del_url(line):
    return re.sub(r'(\S*(\.com).*)|(https?:\/\/.*)', "", line)
# replace tag
def checktag(line): 
    return re.sub(r'\@\S*', "", line)
# Some special charactor
def checkSpecial(line):
    return line.replace('♡', 'love ').replace('\"','')

if __name__ == '__main__': 
# Sentiment 140 example
    # s = '{"data": [{"text": "I love Titanic."},{"text": "I hate Titanic."}]}' # 2 short text that we want to do sentiment analysis
    # response = urllib2.urlopen('http://www.sentiment140.com/api/bulkClassifyJson', s) # request to server     
    # page = response.read() # get the response     
    # print page # print the result     
    # json.loads(page) # parse the result. The result is in JSON format
# example finish

    # Saving file
    emotion_tweets_file = open('./organized/date_sentiment_tweets', 'a')
    
    tweets_buffer = []

    sentiment_dict = {
                    0:-1,
                    2: 0,
                    4: 1
                    }

    def sendto140(line_split = None):
        query_string = '{"data": ['
        # username, date, datetime, content 
        if line_split == None:
            for tweet_list in tweets_buffer:
                query_string += '{"text": "' + tweet_list[3].strip() + '"},'
        else:
            query_string += '{"text": "' + checkSpecial(checktag(del_url(line_split[3].strip()))) + '"},'

        query_string = query_string[:-1] + ']}'

        try:
            response = urllib2.urlopen('http://www.sentiment140.com/api/bulkClassifyJson', query_string) # request to server     
            page = response.read() # get the response     
            # print page # print the result     
            query_result = json.loads(page) # parse the result. The result is in JSON format
            emotion_tweets_file.write('{}\t{}\t{}\t{}\t{}\n'.format(line_split[0], line_split[1], line_split[2], line_split[3].strip(), sentiment_dict[query_result["data"][0]["polarity"]]))
        except:
            print("Fail : "+query_string)
            emotion_tweets_file.write('{}\t{}\t{}\t{}\t{}\n'.format(line_split[0], line_split[1], line_split[2], line_split[3].strip(), 0))

    # Prepare the query tweets
    print('Loading Daily Tweets..')
    with open('./organized/date_tweets') as tweets:

        file_lines = tweets.readlines()
        totalLines = len(file_lines)
        process = 0
        for line in file_lines:
            sendto140(line.split('\t'))
            process += 1
            print("Already process " + str(process) + '/' + str(totalLines))
            # Try to send multi
            # tweets_buffer.append(line.split('\t'))
            # if len(tweets_buffer) > 4:
            #     sendto140()
            #     process += 5
            #     print("Already process " + str(process) + '/' + str(totalLines) + ", Sleep for 2 sec..")
            #     time.sleep(1)
            #     tweets_buffer = []

    emotion_tweets_file.close()
    print('Finished! \n')