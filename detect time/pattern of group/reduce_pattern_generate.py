# -*- coding: utf8 -*-
import sys
import fileinput

if __name__ == '__main__':
    oldword, acc = '***', 0
    for line in fileinput.input():
        split_line = line.strip().split('\t')
        pattern, count = split_line
        if pattern != oldword:
            if acc > 0:
                print('{}\t{}'.format(oldword, str(acc)))
                # out.write('{}\t{}\t{}\n'.format(user,oldword, str(acc)))
            oldword, acc = pattern, 0
        acc += int(count)
    fileinput.close()