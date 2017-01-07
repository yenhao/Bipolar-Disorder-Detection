from time import time
from time import sleep
from twython import Twython
from twython import TwythonAuthError
from twython import TwythonRateLimitError
from twython import TwythonError
from warnings import warn
from datetime import datetime
import math


# import config
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

def removelinechange(sentence):
    result = sentence.replace('\n',' ')
    result = result.replace('\r', ' ')
    return result


def searchKeyword(keyword = '', lang = 'en', max_id = ''):
    twitter = Twython( consumer_key, consumer_secret,access_token,access_token_secret )

    while(True):
        try:
            if(max_id == ''):
                searchResult = twitter.search(q=keyword, lang='en')
            else:
                print('Max ID: ' + max_id)
                searchResult = twitter.search(q=keyword, lang='en', max_id = max_id, include_entities=1)
            
            return searchResult
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

def findBetween(sentence, begin, end):
    return sentence[sentence.find(begin)+len(begin):sentence.find(end)]


if __name__ == '__main__':

    keyword = 'YOUR KEY WORD'
    print('\n\nStart searching keyword: %s \n\n'% keyword) 

    i = 0
    with open('crawl_patients',"a") as outfile:
        search_result = searchKeyword(keyword = keyword)
        while True:

            result_json = search_result['statuses']
            out_content = ''
            for result in range(len(result_json)):
                text = removelinechange(result_json[result]['text'].encode('utf-8'))
                # I don't want retweets
                if text [:2] =='RT':
                    continue
                content = "{}\t{}\t{}\t{}\n".format(result_json[result]['user']['screen_name'], result_json[result]['created_at'], text, result_json[result]['id_str'])
                out_content += content
                print(content)
            outfile.write(out_content)
            i+=1

            print('\n\nFinish %s Round Search! Sleep for 10 seconds\n\n'% str(i))
            sleep(10)
            # Next Round
            try:
                next_result = search_result['search_metadata']['next_results']
            except:
                print('Ending')
                break
            max_id = findBetween(next_result, '?max_id=', '&q=')
            search_result = searchKeyword(keyword, max_id = max_id)
