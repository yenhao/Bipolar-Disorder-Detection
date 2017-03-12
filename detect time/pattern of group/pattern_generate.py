# -*- coding: utf8 -*-
import os
import re
import multiprocessing as mp
from collections import defaultdict
from nltk.tokenize import TweetTokenizer
import itertools
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

def slideWindows(token_list, size = 3):
    if len(token_list) >= size:
        return getPatternCombination(token_list[:3]) + slideWindows(token_list[1:], size)
    else:
        return []

def getPatternCombination(pattern_word_list):
    pattern_list = []
    for i in range(3):
        temp_pattern_word_list = list(pattern_word_list)
        temp_pattern_word_list[i] = '<.>'
        pattern_list.append(' '.join(temp_pattern_word_list))

    return pattern_list

def matchPattern(pattern, all_text_list):
    pattern_token = pattern.replace('.','\.').replace('(','\(').replace(')','\)').replace('$','\$').replace('^','\^').split(' ')
    pattern_token[pattern_token.index('<\.>')] = '(?!\#|\@)\S+'
    word_counts = 0
    for user_tweet_list in all_text_list:
        for tweets in user_tweet_list:
            try:
                words = re.findall(' '.join(pattern_token) ,tweets)
            except:
                words = []
            word_counts += len(words)
    return (pattern, word_counts)

def LinetoPattern(tweets_list):
    """Read a list and return a sequence of (pattern, occurances) values.
    """
    # print multiprocessing.current_process().name, 'reading', filename
    output = []
    for line in enumerate(tweets_list[0]):
        token_list = line.split(' ')
        # Go through new pattern
        for pattern in slideWindows(token_list):
            output.append( (pattern, 1) )
    return output


def count_pattern(item):
    """Convert the partitioned data for a word to a
    tuple containing the word and the number of occurances.
    """
    pattern, occurances = item
    return (pattern, sum(occurances))

def partition(self, mapped_values):
    """Organize the mapped values by their key.
    Returns an unsorted sequence of tuples with a key and a sequence of values.
    """
    partitioned_data = collections.defaultdict(list)
    for key, value in mapped_values:
        partitioned_data[key].append(value)
    return partitioned_data.items()

if __name__ == '__main__':
    # Using all cpu core -1
    pool = mp.Pool(processes=mp.cpu_count()-1)
    

    # folder = '../../twitter crawler/regular/'
    folder = '../patient emo_senti/'
    out_name = 'regular_user'
    print("Load User Tweets")
    print(folder)
    all_text_list = [loadTweets( folder, user) for user in checkFolderFile(folder)]

    # print len(all_text_list) # file counts
    dead_word_file = open('Dead_word_regular','w')

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
    pattern_dict = defaultdict(lambda : 0)
    print('Go through Bipolar Pattern')
    for i, user_tweet_list in enumerate(all_text_list):
        for line in user_tweet_list:
            token_list = line.split(' ')
            # Go through new pattern
            for pattern in slideWindows(token_list):
                bipolar used
                if pattern not in pattern_dict:
                    multi_res =[pool.apply_async(matchPattern, (pattern, all_text_list[i:],)) for user_tweet_list in all_text_list[i:]]
                    pattern_sum = sum([res.get() for res in multi_res])
                    print('\n{}\t{}\t{}'.format(i, pattern.encode('utf-8'), pattern_sum))
                    pattern_dict[pattern] = pattern_sum

    # Output to file
    sorted_pattern_dict = sorted(pattern_dict.items(), key=operator.itemgetter(1), reverse=True)
    with open(out_name,'w') as outfile:
        for pattern, count in sorted_pattern_dict:
            outfile.write('{}\t{}\n'.format(pattern.encode('utf-8'), count))


