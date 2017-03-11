# -*- coding: utf8 -*-
from nltk.tokenize import TweetTokenizer

from collections import defaultdict
import re
import sys, gzip, re, os, fileinput

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

if __name__ == '__main__':
    pattern_dict = defaultdict(lambda : 0)

    tknzr = TweetTokenizer()
    for line in fileinput.input():
        split_line = line.split('\t')
        if len(split_line) != 2: continue

        uid, text = split_line
        token_list = tknzr.tokenize(checkline(text).lower())
        for pattern in slideWindows(token_list):
            pattern_dict[pattern] += 1

    for pattern, count in pattern_dict.items():
        print('{}\t{}'.format(pattern.encode('utf-8'), count))