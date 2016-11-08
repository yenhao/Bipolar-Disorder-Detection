
# coding: utf-8


# function to delete url
def del_url(line):
    seg_result = ''
    for seg in line.split(' '):
#     if the split-part contain url, make this segment to be '' empty
        if seg[:7] == 'http://' or seg[:8] == 'https://':
            seg = ''
#     re-assemble the sentence
        seg_result += seg + ' '
    return seg_result

buffer_line = []

# buffer
def buffer_write(line):
    global buffer_line
    global output_file
    buffer_line += [line]
    if len(buffer_line) >= 100:
        buffer_write = ''
        for each_line in buffer_line:
            buffer_write += each_line.strip() + '\n'
        output_file.write(buffer_write)
        buffer_line = []

output_file = open ('after_preprocessing_file','w')
with open('before_preprocessing_file') as text_file:
    for line in text_file.readlines():
        uid = line.split('\t')[0]
        content = line.split('\t')[1]
#         send to the buffer after delete url
        buffer_write(uid + '\t' +del_url(content))
    
#     clean the buffer
    buffer_last = ''
    for each_line in buffer_line:
        buffer_last += each_line.strip() + '\n'
    output_file.write(buffer_last)

