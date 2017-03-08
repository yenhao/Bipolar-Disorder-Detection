# -*- coding: utf8 -*-
import os
import re
import multiprocessing as mp
from collections import defaultdict
from nltk.tokenize import TweetTokenizer
import operator
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
    return line.replace('♡', 'love ').replace('\"','').replace('“','').replace('”','').replace('…','...').replace('—','-')

def checkline(line):
    return del_url(checkhashtag(checktag(checkSpecial(line))))

def checkFolderFile(folder):
    return os.listdir(folder)

def loadTweets(folder, filename):
    with open(folder + filename, 'r') as openfile:
        return [checkline(line.strip().split('\t')[3]) for line in openfile.readlines()]

def combineWordToken(token_list):
    combine_list = ["n't","'m","'s"]
    for i, token in enumerate(token_list):
        if len(token_list) -i == 1: continue
        if token_list[i+1] in combine_list:
            token_list[i:i+2] = [''.join(token_list[i:i+2])]
    return token_list

# def whitespaceTokenizer(line):
#     return [token.lower() for token in line.split(' ') if token != '']

def slideWindows(token_list, size = 3):
    if len(token_list) > size:
        return getPatternCombination(token_list[:3]) + slideWindows(token_list[2:], size)
    else:
        return []

def getPatternCombination(pattern_word_list):
    pattern_list = []
    for i in range(3):
        temp_pattern_word_list = list(pattern_word_list)
        temp_pattern_word_list[i] = '<.>'
        pattern_list.append(' '.join(temp_pattern_word_list))

    return pattern_list

def matchPattern(pattern, user_tweet_list = []):
    pattern_token = pattern.replace('.','\.').replace('(','\(').replace(')','\)').replace('$','\$').replace('^','\^').split(' ')
    pattern_token[pattern_token.index('<\.>')] = '(?!\#|\@)\S+'
    word_counts = 0
    for tweets in user_tweet_list:
        try:
            words = re.findall(' '.join(pattern_token) ,tweets)
        except:
            words = []
        word_counts += len(words)
    return word_counts

if __name__ == '__main__':
    # Using all cpu core -1
    pool = mp.Pool(processes=mp.cpu_count()-1)
    

    # folder = '../../twitter crawler/patient_tweets/'
    folder = '../patient emo_senti/'
    out_name = 'Bipolar Pattern Year'
    print("Load User Tweets")
    print(folder)
    all_text_list = [loadTweets( folder, user) for user in checkFolderFile(folder)[:1]]

    # print len(all_text_list) # file counts
    dead_word_file = open('Dead_word','w')

    print('Tokenize every tweets')
    tknzr = TweetTokenizer()
    for i, user_tweet_list in enumerate(all_text_list):
        for j, line in enumerate(user_tweet_list):
            try:
                token_list = tknzr.tokenize(line.lower())
            except:
                dead_word_file.write(line)
                token_list = []
            all_text_list[i][j] = ' '.join(token_list)

    dead_word_file.close()

    # dict{ pattern : count}
    pattern_dict = defaultdict(lambda : None)
    print('Go through Pattern')
    for i, user_tweet_list in enumerate(all_text_list):
        for line in user_tweet_list:
            token_list = line.split(' ')
            # Go through new pattern
            for pattern in slideWindows(token_list):
                if pattern not in pattern_dict:
                    # print [matchPattern(pattern, user_tweet_list) for user_tweet_list in all_text_list]
                    multi_res =[pool.apply_async(matchPattern, (pattern, user_tweet_list,)) for user_tweet_list in all_text_list]
                    pattern_sum = sum([res.get() for res in multi_res])
                    print('\n{}\t{}\t{}'.format(i, pattern.encode('utf-8'), pattern_sum))
                    pattern_dict[pattern] = pattern_sum

    # Output to file
    sorted_pattern_dict = sorted(pattern_dict.items(), key=operator.itemgetter(1), reverse=True)
    with open(out_name,'w') as outfile:
        for pattern, count in sorted_pattern_dict:
            outfile.write('{}\t{}\n'.format(pattern.encode('utf-8'), count))


