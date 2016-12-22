import os

# to get the file name list in your file location
def get_folder_file_list(folder):
	 return [folder_file for folder_file in os.listdir(folder+'/')]

def filter_profile_by_keywords(profile, keyword_list):
	for keyword in keyword_list:
		if keyword in profile: return True
		else: return False

# for each file get the profile and get user who have the keyword
file_folder = 'YOUR FILE FOLDER'
keyword = [YOUR FILTER KEYWORD LIST]
valid_user_dict={}
for file in get_folder_file_list(file_folder):
	# print('\n\n****'+ file + '****')
	with open(file_folder + '/' + file) as open_file:
		for line in open_file.readlines():
			userID, screenname, created_time,profile = line.split('\t')
			if filter_profile_by_keywords(profile,keyword): 
				if userID in valid_user_dict: continue
				valid_user_dict[userID] = (screenname,created_time,profile)

# print(len(valid_user_dict))
with open(file_folder + "/temp_user",'w') as out_file:
	for key, value in valid_user_dict.items():
		out_line = "{} \t {}\n".format(key,value)
		out_file.write(out_line)
