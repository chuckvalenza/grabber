# Grabber

## Overview

I created this to download files off of my VPS which were uploaded from my home
server. The complete.py script is designed to be executed once the VPS has
completed its download of the target file. It assumes you have two directories:
'finished' and 'data' and you have established an ssh config file and key login
for the host which you want to grab files from.

Each of these two should have subdirectories by category: i.e. "taxes" or
"pictures"

Your files should be stored in the ./data/\<category\>/ directory. A
corresponding file will be created with the exact name in the 'finished'
directory once complete.py is executed. autodl.py simply checks these
directories and grabs them. There is support for multiple grabbers, just add
them to the GRABBERS global as strings. The signal files will not be deleted
until all grabbers have grabbed the file.

## Usage

```
python3 complete.py <category> example] [file name (2015).txt
```

```
python3 grabber.py <Host shortname> <category1> <category2>
```

