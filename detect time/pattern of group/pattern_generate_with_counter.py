# -*- coding: utf8 -*-
import os
import re
import multiprocessing as mp
from collections import defaultdict, Counter
from nltk.tokenize import TweetTokenizer
import operator
from time import gmtime, strftime

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
    return line.replace('♡', 'love ').replace('\"','').replace('“','').replace('”','').replace('…','...').replace('—','-').replace('’','\'')

def checkline(line):
    return del_url(checktag(checkSpecial(line)))

def checkFolderFile(folder):
    return os.listdir(folder)

def loadTweets(folder, filename, text_loc = -1):
    with open(folder + filename, 'r') as openfile:
        return [checkline(line.strip().split('\t')[text_loc]) for line in openfile.readlines()]

def combineWordToken(token_list):
    combine_list = ["n't","'m","'s"]
    for i, token in enumerate(token_list):
        if len(token_list) -i == 1: continue
        if token_list[i+1] in combine_list:
            token_list[i:i+2] = [''.join(token_list[i:i+2])]
    return token_list

def slideWindows(token_list, size = 3, combine = True):
    if len(token_list) >= size:
        if combine == True:return getPatternCombination(token_list[:size], size) + slideWindows(token_list[1:], size)
        else: return [' '.join(token_list[:size])] + slideWindows(token_list[1:], size, combine)
    else:
        return []

def getPatternCombination(pattern_word_list, size):
    pattern_list = []
    for i in range(size):
        temp_pattern_word_list = list(pattern_word_list)
        temp_pattern_word_list[i] = '<.>'
        pattern_list.append(' '.join(temp_pattern_word_list))

    return pattern_list

def matchPattern(pattern, user_tweet_list):
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

def getPattern(user_tweet_list, size = 3, combine = True):
    return [pattern for token_list in user_tweet_list for pattern in slideWindows(token_list, size, combine)]

def partition(text_list, chunk = 5):
    chunksize = len(text_list)/chunk
    start = 0
    result_list = []
    for _ in xrange(chunk):
        end = start+chunksize
        if len(text_list) < end+chunksize: result_list.append(text_list[start:])
        else: result_list.append(text_list[start:end])
        start = end
    return result_list

if __name__ == '__main__':
    # Using all cpu core -1
    pool = mp.Pool(processes=mp.cpu_count()-1)
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    # folder = '../../twitter crawler/regular/' # For single file
    # file = 'regularUser_en_fixed.txt' # For single file
    folder = '../patient emo_senti/' # for multi files
    out_name = 'bipolar hashtag_3gram'
    print("Load User Tweets from {}".format(folder))
    # all_text_list = [loadTweets(folder, file)] # For single file

    all_text_list = [loadTweets( folder, user, text_loc = 3) for user in checkFolderFile(folder)] # for multi files
    print('File Count: {}'.format(len(all_text_list)))

    print('Tokenizing every tweets')
    tknzr = TweetTokenizer()
    dead_word_file = open('Dead_word','w')
    for i, user_tweet_list in enumerate(all_text_list):
        for j, line in enumerate(user_tweet_list):
            try:
                token_list = tknzr.tokenize(line.lower())
            except:
                dead_word_file.write(line)
                token_list = []
            all_text_list[i][j] = token_list
    dead_word_file.close()

    print('Sliding Windows')
    # new_text_list = partition(all_text_list[0], chunk = mp.cpu_count()-1) # For single file
    # del all_text_list # For single file
    # multi_res = [pool.apply_async(getPattern, (part_list,)) for part_list in new_text_list] # For single file
    # new_text_list = None # For single file

    multi_res = [pool.apply_async(getPattern, (user_tweet_list, 3, True,)) for user_tweet_list in all_text_list] # for multi files
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    print('Put Pattern from {} chunks to Counter'.format(len(multi_res)))
    pattern_counter = Counter([pattern for res in multi_res for pattern in res.get()])
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    print('Total {} patterns'.format(len(pattern_counter)))
    print('Output to file')
    # Output to file
    with open(out_name,'w') as outfile:
        for pattern, count in pattern_counter.most_common():
            outfile.write('{}\t{}\n'.format(pattern.encode('utf-8'), count))