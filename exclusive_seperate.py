import operator
from collections import defaultdict
import math

def ReadFileToDict(filename):
    with open('WordCount/result_'+filename+'.txt') as inputfile:
        input_dict = {line.split('\t')[0]:int(line.split('\t')[1]) for line in inputfile.readlines()}   
    return input_dict

def getExclusiveDict(compare_dict, basic_dict):
    result_dict = {}
    # sorted_compare = sorted(compare_dict.items(), key=operator.itemgetter(1), reverse = True)
    for word in compare_dict:
        if word not in basic_dict:
            result_dict[word] = compare_dict[word]
    return result_dict

def wordCountInDict(in_dict):
    total_count = 0
    for key in in_dict:
        total_count += in_dict[key]
    return total_count
   
def normalizeByUser(compare_file,exclusive_dict):
    # create the user word dict first
    userword_dict = defaultdict(lambda : defaultdict(lambda : 0))
    with open('user_word_count/'+compare_file+'.txt') as user_file:
        for line in user_file.readlines():
            userID, word, count = line.split('\t')
            userword_dict[word][userID] = int(count)
    # Try to normalize each word
    for word in exclusive_dict:
        # if the word is in userword_dict
        # do the normalize and change the value of exclusive_dict
        # only count by how many user
        if word in userword_dict:
            exclusive_dict[word] = len(userword_dict[word])
    return exclusive_dict
        


basic_file = 'regularUser_en_fixed'
# bipolar_experts BPD bipolar bb_mix
compare_file = 'bipolar'

print(compare_file)


basic_dict = ReadFileToDict(basic_file)
compare_dict = ReadFileToDict(compare_file)


exclusive_dict = getExclusiveDict(compare_dict,basic_dict)

# Normalize by user
# Because some word may just used by single user
normalized_exclusive_dict = normalizeByUser(compare_file,exclusive_dict)

with open('exclusive/normalized_'+compare_file,'w') as out_file:
    sorted_exclusive_dict = sorted(normalized_exclusive_dict.items(), key=operator.itemgetter(1), reverse = True)
    for word in sorted_exclusive_dict:
        out_file.write(word[0] + '\t' + str(word[1]) + '\n')