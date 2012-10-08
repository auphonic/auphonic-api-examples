#! /bin/bash
#
# This script allows you to start production with multiple files
# on your auphonic account.
# It can be used to batch process many files at once.
#
# It uses the Auphonic API for batch processing:
# https://auphonic.com/developers
#
# USAGE:
# batch-upload.sh [filenames]
#
# EXAMPLE:
# batch-upload.sh file1.mp3 file2.m4a file3.mp3 file4.wav ...
#
# Author: Andre Rattinger
# Date: Sept 2012
#

FILES=$*

# check if there are some files
if [ $# -eq 0 ]
  then
    echo
    echo "Please give us some files :) !"
    echo
    echo "Usage:"
    echo "batch-upload.sh file1.mp3 file2.m4a file3.mp3 file4.wav ..."
    echo
    return
fi

echo
echo "Welcome to the Auphonic upload script!"
echo
echo "Please enter your Auphonic account information:"

read -p "Auphonic Username: " username
read -s -p "Auphonic Password: " password
echo
read -p "Preset UUID: " preset
echo

for f in $FILES
do
    echo "Uploading $f"

    # auphonic API request
    curl -X POST https://auphonic.com/api/simple/productions.json \
        -u "$username:$password" \
        -F "preset=$preset" \
        -F "action=start" \
        -F "input_file=@$f" > /dev/null 2>&1
done

echo
echo "Finished!"
echo "Please check your auphonic account or email for status updates!"
echo
