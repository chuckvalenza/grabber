# complete.py
#
# triggered on torrent complete. creates a symlink to the file to download in the "finished" directory

import sys
from os import listdir, symlink
from os.path import isfile, join, expanduser

# global variables

RTORRENT_DIR = expanduser("~/") + "code/autodl/"
#RTORRENT_DIR = expanduser("~/") + "private/rtorrent/"



# --

category = sys.argv[1]
file_arg = sys.argv[2:]

signal_dir = target_dir = RTORRENT_DIR

#signal_dir = homedir + "private/rtorrent/finished/"
#target_dir = homedir + "private/rtorrent/data/"
signal_dir += "finished/" + category + "/"
target_dir += "data/" + category + "/"

sig_filepath = signal_dir 
tgt_filepath = target_dir + category + "/"

filename=""

i=0
for s in file_arg:
	filename += s
	i += 1
	if i != len(file_arg):
		filename += " "

sig_file_list = [f for f in listdir(signal_dir) if isfile(join(signal_dir, f))]
sig_file = sig_filepath + str(len(sig_file_list))
tgt_file = tgt_filepath + filename

print(sig_file)
print(tgt_file)

symlink(tgt_file, sig_file)

# autodl.py
#
# lists signal files in remote directory, downloads the targets, then destroys the signal file
