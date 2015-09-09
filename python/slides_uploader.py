# -*- coding: utf-8 -*-
'''
Script to upload chapters with chapter images generated from pdf lecture slides.

Usage:
  python slides_uploader.py your_chapters_file.txt your_slides.pdf

This script does not start a production. It just creates a new Auphonic
production and adds chapters from your_chapters_file.txt.
All slides in your_slides.pdf will be added as chapter images to the
production:
First slide will be converted to an image and added to the first chapter,
second slide will be added as chapter image to the second chapter etc.
Please edit (add audio file, apply preset, etc.) and start the production in
our web interface afterwards!

IMPORTANT:
You have to install ImageMagic on your system!
Download it here: http://www.imagemagick.org/

2015, Georg Holzmann (grh@auphonic.com)

'''

import sys
import os
from os.path import splitext, basename, join
from tempfile import mkdtemp
from shutil import rmtree
import glob
import re
import urllib2
import json
import base64
import getpass


# Please edit all variables within SETTINGS to match your setup!

###############################################################################
# SETTINGS

# convert command of imagemagick
# NOTE: you can also set an absolute path if necessary (windows)!
CONVERT_CMD = "convert"

# END of SETTINGS
###############################################################################


# temporary directory for various files
TEMP_DIR = None


def convert_pdf_to_chapter_images(pdf_slides):
    """ Converts the pdf slides to individual jpeg chapter images.
    """
    target_img = join(TEMP_DIR, splitext(basename(pdf_slides))[0] + "-%03d.jpg")

    # create and run imagemagic command to convert pdf to jpeg
    cmd = "%s -density 300 %s -quality 86 %s" % (
        CONVERT_CMD, pdf_slides, target_img
    )
    print("\nConverting pdf slides to images:")
    #print(cmd)
    os.system(cmd)

    # get all slides
    slide_images = glob.glob(target_img[:-9] + "-*.jpg")
    slide_images.sort()
    print("\tNr. of slides: %d" % len(slide_images))

    # we could not generate slides
    if len(slide_images) == 0:
        print("\nNo slides could be extracted from: %s!" % pdf_slides)
        print("Please double-check that imagemagic (convert) is installed and in your path!")
        print("Download it here: http://www.imagemagick.org/\n")
        exit(-1)

    return slide_images


def parse_chapter_marks_file(chapter_file):
    """ Parses chapter mark file to extract start time, title and url.
    """
    chapters = []

    # open chapter marks file
    f = open(chapter_file, "r")

    print("\nParsing chapters file:")

    try:
        # replace all \r with \n (universal newline) to avoid some problems,
        # then get lines
        data = f.read().replace('\r\n', '\n').replace('\r', '\n')
        lines = data.split('\n')

        for line in lines:
            # strip any non-digit chars at the beginning of the line
            # (e.g. a BOM at the beginning)
            line = re.sub("^\D+", "", line)

            words = len(line.split())

            # ignore empty lines
            if words == 0:
                continue

            elif words == 1:
                # strip newline characters at the end
                timestring = line.rstrip("\n")
                timestring = line.rstrip("\r")  # carriage return (windows)
                title = "No Title"
                url = None

            else:
                # split on first whitespace
                timestring, title = re.split("\s+", line, 1)
                title = title.rstrip("\n")
                title = title.rstrip("\r")

                # try to extract URLs
                if '<' in title and '>' in title:
                    title, url = title.split('<')
                    url = url.rstrip('>')
                    title = title.rstrip(' ')
                else:
                    url = None

            chapters.append([timestring, title, url])

    finally:
        f.close()

    print("\tNr. of chapters: %d" % len(chapters))

    return chapters


def create_production(username, password, chapters, slide_images):
    """ Create a production with given chapters and slides.
    """
    # create chapters metadata
    chapters_data = []
    nr_images = len(slide_images)
    for i, c in enumerate(chapters):
        dd = {"start": c[0], "title": c[1], "url": c[2]}

        # add image data if we have enough slides
        if i < nr_images:
            dd["image"] = base64encode_image_file(slide_images[i])

        chapters_data.append(dd)

    print("\nCreate Auphonic Production and Upload Chapters Data:")

    # create the new production
    url = "https://auphonic.com/api/productions.json"
    data = {
        "metadata": {"title": "CHANGEME: Slides Upload"},
        "chapters": chapters_data,
    }
    response = post_request(url, data, username, password)

    # get UUID of our production
    if response["status_code"] == 200:
        print("\tSUCCESS!")
        uuid = response["data"]["uuid"]
        edit_page = response["data"]["edit_page"]

        print("\n\nThe following production was created:")
        print(uuid)

        print("\nPlease edit and start the production here:")
        print(edit_page)
        print("")

    else:
        # there was a problem
        print("\tFAILED!")
        print("\n\nError Message:")
        print(response)
        print("")


def base64encode_image_file(filename):
    """ Base64 encodes an image file into a string.
    """
    with open(filename) as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string


def post_request(url, data, username, password):
    """ POST request with JSON data and HTTP Basic Authentication.
    """
    data_json = json.dumps(data)
    header = {'Content-Type': 'application/json'}

    req = urllib2.Request(url, data_json, header)
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    req.add_header("Authorization", "Basic %s" % base64string)
    response = urllib2.urlopen(req).read()

    return json.loads(response)


if __name__ == "__main__":
    """ Main function.
    """
    # check if we have correct arguments
    if len(sys.argv) != 3:
        print("\nUsage:")
        print("python slides_uploader.py your_chapters_file.txt your_slides.pdf\n")
        exit(-1)

    chapter_file = sys.argv[1]
    pdf_slides = sys.argv[2]

    print("\nPlease enter your Auphonic account information:")
    username = raw_input('Auphonic Username: ')
    password = getpass.getpass("Auphonic Password: ")

    try:
        # create a temporary directory
        TEMP_DIR = mkdtemp()

        # convert slides to pdf and parse chapters file
        slide_images = convert_pdf_to_chapter_images(pdf_slides)
        chapters = parse_chapter_marks_file(chapter_file)

        # create a production with given chapters and slides
        create_production(username, password, chapters, slide_images)

    finally:
        # clean-up temporary files
        rmtree(TEMP_DIR)
