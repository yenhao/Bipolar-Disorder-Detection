# encoding utf8
import os
from collections import defaultdict
import math
# get the dictionary of file
# file sytnax = pattern,freq (first line is attribute)
def get_common_word_dict(file_name):
    with open(file_name) as open_file:
        open_file = open_file.readlines()[2:]
        freq_count = 0
        # to get the total count
        for line in open_file:
            freq_count += int(line.split(',')[1])
        # get each pattern and normalize the freq
        file_dict = {}
        for line in open_file:
            key, freq = line.split(',')
            # save pattern freq to dictionary also normalize freq
            file_dict[key] = float(freq)/freq_count
        return file_dict
# Compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)
def cosine_similarity(v1,v2):
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)

# to get the file name list in the folder
folder_file_list = [folder_file for folder_file in os.listdir('your csv directory') if folder_file[-3:] == 'csv']
folder_file_dict = {}
for folder_file in folder_file_list:
    folder_file_dict[folder_file] = get_common_word_dict(folder_file)
# fill in attribute list
attr_list = []
for folder_file in folder_file_dict:
    for each_attr in folder_file_dict[folder_file]:
        if each_attr not in attr_list:
            attr_list.append(each_attr)
# create defaultdict and initialize the default list as the length of attr_list
file_freq_list_dict = defaultdict(lambda : [0]*len(attr_list))
#according to attribute list, fill in the normalized freq value for each file
for folder_file in folder_file_dict:
    for each_pattern, value in folder_file_dict[folder_file].iteritems():
        file_freq_list_dict[folder_file][attr_list.index(each_pattern)] = value
# Calculate similarity
for each_compare in folder_file_list:
    for each_compared in folder_file_list[folder_file_list.index(each_compare)+1:]:
        print 'Similarity -> ' + each_compare + ' & ' + each_compared + ' : ' + str(cosine_similarity(file_freq_list_dict[each_compare],file_freq_list_dict[each_compared]))
