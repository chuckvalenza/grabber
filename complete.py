#!/usr/bin/env python3

# complete.py
#
# triggered on torrent complete. creates a symlink to the file to download in the "finished" directory

import os
import sys
from os import listdir, symlink
from os.path import isfile, join, expanduser

# global variables

DL_DIR = expanduser("~/") + "private/rtorrent/"

# --

category = sys.argv[1]
file_arg = sys.argv[2:]

signal_dir = DL_DIR + "finished/" + category + "/"
sig_filepath = signal_dir 

filename=""
i=0
for s in file_arg:
	filename += s
	i += 1
	if i != len(file_arg):
		filename += " "

sig_file_list = [f for f in listdir(signal_dir) if isfile(join(signal_dir, f))]
sig_file = sig_filepath + filename

open(sig_file, 'a')

