# encoding utf8
import os

# get the dictionary of file
# file sytnax = pattern,freq (first line is attribute)
def get_common_word_dict(file_name):
    with open(file_name) as open_file:
        open_file = open_file.readlines()[2:]
        freq_count = 0
        for line in open_file:
            freq_count += int(line.split(',')[1])
        file_dict = {}
        for line in open_file:
            key, freq = line.split(',')
            # save pattern freq also normalize freq
            file_dict[key] = float(freq)/freq_count
        return file_dict

# to get the file name list in the folder
folder_file_list = [folder_file for folder_file in os.listdir(".") if folder_file[-3:] == 'csv']

folder_file_dict = {}
for folder_file in folder_file_list:
    folder_file_dict[folder_file] = get_common_word_dict(folder_file)

# fill in attribute list
attr_list = []
for folder_file in folder_file_dict:
    for each_attr in folder_file_dict[folder_file]:
        if each_attr not in attr_list:
            attr_list.append(each_attr)
# print attr_list.index('ernllysmiling-I')
# print len(attr_list)
file_freq_list_dict = {}
