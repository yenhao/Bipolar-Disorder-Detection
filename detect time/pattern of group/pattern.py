# -*- coding: utf8 -*-
import os
import re
import multiprocessing as mp
from collections import defaultdict
import nltk
# function to delete url
def del_url(line):
    return re.sub(r'(\S*(\.com).*)|(https?:\/\/.*)', "", line)
# replace tag
def checktag(line): 
    return re.sub(r'\@\S*', "@", line)

def checkhashtag(line): 
    return re.sub(r'\#\S*', "#", line)

# Some special character
def checkSpecial(line):
    return line.replace('♡', 'love ').replace('\"','').replace('“','').replace('”','').replace('…','...')

def checkline(line):
    return del_url(checkhashtag(checktag(checkSpecial(line))))

def checkFolderFile(folder):
    return os.listdir(folder)

def loadTweets(folder, filename):
    with open(folder + filename, 'r') as openfile:
        return [checkline(line.strip().split('\t')[-1]) for line in openfile.readlines()]

def combineWordToken(token_list):
    combine_list = ["n't","'m","'s"]
    for i, token in enumerate(token_list):
        if len(token_list) -i == 1: continue
        if token_list[i+1] in combine_list:
            token_list[i:i+2] = [''.join(token_list[i:i+2])]
    return token_list

# def whitespaceTokenizer(line):
#     return [token.lower() for token in line.split(' ') if token != '']

def slideWindows(token_list, pattern_dict, size = 3):
    if len(token_list) > size:
        pattern_dict[' '.join(token_list[:3])] = 0
        slideWindows(token_list[2:], pattern_dict, size)
    else:
        return True
    
if __name__ == '__main__':

    folder = '../../twitter crawler/patient_tweets/'

    print("Load User Tweets")
    print(folder)
    all_text_list = [loadTweets( folder, user) for user in checkFolderFile(folder)[:2]]

    # print len(all_text_list) # file counts

    # dict{ pattern : count}
    pattern_dict = defaultdict(lambda : None)

    for user_tweet_list in all_text_list:
        for line in user_tweet_list:
            # token_list = whitespaceTokenizer(line)
            # token_list = re.findall(r'[.?]|\w+', line.lower())
            token_list = combineWordToken(nltk.word_tokenize(line.lower().decode('utf-8')))
            slideWindows(token_list, pattern_dict)

    for key in pattern_dict:
        print key

