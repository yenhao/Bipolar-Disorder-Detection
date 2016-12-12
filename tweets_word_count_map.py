import sys, gzip, re, os, fileinput
from collections import defaultdict
# cat <input_file> | ./lmr 8m 8 'python3 tweets_word_count_map.py' 'python3 tweets_word_count_reduce.py' <output_folder>
# to get # or @ in line
def tokens(str1): return re.findall('\@?\#?[a-zA-Z0-9]+\'?[a-zA-Z0-9]+\.*', str1)
# to remove url
def del_url(line): return re.sub(r'https?:\/\/.*', "", line)

def checktag(list1): 
    ans_list = []
    for item in list1:
        if item[0] == '@':
            item = '<user>'
        elif item[0] == '#':
            item = '#' + item[1:].lower()
        else:
            item = item.lower()
        ans_list.append(item)
    return ans_list
# str = 'wwe ivory naked #sandra teen model topless @yenhao0218'

# print(checktag(tokens(str)))
# def tokenize(aline):
#     word_list = [aline.split(' ') ]

user_word_count_dict = defaultdict(lambda : defaultdict(lambda : 0))
for line in fileinput.input():
    split_line = line.split('\t')
    if len(split_line) != 2: continue
    uid, text = split_line
    for word in checktag(tokens(del_url(text))):
        user_word_count_dict[uid][word] += 1 
for user in user_word_count_dict:
    for word in user_word_count_dict[user]:
        print(word + '\t' + str(user_word_count_dict[user][word]))
        # out.write(user + '\t' + word + '\t' + str(user_word_count_dict[user][word]) + '\n')
# out.close()