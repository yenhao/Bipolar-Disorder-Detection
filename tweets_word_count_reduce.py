import sys

oldword, acc = '***', 0

import fileinput

for line in fileinput.input():
    split_line = line.strip().split('\t')
    # if len(split_line) != 3 : continue
    word, count = split_line
    # print (split_line)
    # if user != olduser:
    if word != oldword:
        if acc > 0:
            print('{}\t{}'.format(oldword, str(acc)))
            # out.write('{}\t{}\t{}\n'.format(user,oldword, str(acc)))
        oldword, acc = word, 0
    acc += int(count)
fileinput.close()
# out.close()