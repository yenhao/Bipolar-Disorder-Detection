import sys, os

if len(sys.argv) < 3 :
    print ('Format')
    # print 'python image.py <input file> <output file>'
    print ('python image.py <map_reduce result folder> <result_folder>')
    sys.exit()

folder = sys.argv[1]
out_folder = sys.argv[2]

# to get the file name list in your file location
folder_file_list = [folder_file for folder_file in os.listdir(folder+'/') if folder_file[:7] == 'reducer']

final_content = []
for everyfile in range(len(folder_file_list)):
    input_file_name = folder_file_list[everyfile]

    print ('Merging ' + input_file_name + '..')
     
    with open(folder + '/' + input_file_name) as open_file:
        final_content += [ '{}\n'.format(line.strip()) for line in open_file.readlines()]

# make sure have output folder
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

with open(out_folder+'/'+folder+'.txt','w') as out_file:
    output_content = ''
    for each_line in final_content:
        output_content += each_line
    out_file.write(output_content)