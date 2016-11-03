# coding: utf-8

# remove url
def del_url(line):
    seg_result = ''
    for seg in line.split(' '):
        if seg[:7] == 'http://' or seg[:8] == 'https://':
            seg = ''
        seg_result += seg + ' '
    return seg_result

def buffer_write(line):
    global buffer_line
    global output_file
    buffer_line += [line]
    if len(buffer_line) >= 10:
        buffer_write = ''
        for each_line in buffer_line:
            buffer_write += each_line + '\n'
        output_file.write(buffer_write)
        buffer_line = []

buffer_line = []
output_file = open ('dataset/pre_bb_mix.txt','w')

with open('dataset/dump_bb_mix.txt') as text_file:

    for line in text_file.readlines():
        uid,content = line.split('\t')
        buffer_write(uid + '\t' +del_url(content))
        
    for each_line in buffer_line:
        buffer_write += each_line + '\n'
    output_file.write(buffer_write)



