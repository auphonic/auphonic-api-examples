# -*- coding: utf-8 -*-
'''
This script allows you to export all your soundcloud files to auphonic
and distribute it to another server, like YouTube.

It uses the Auphonic API for batch processing:
https://auphonic.com/developers

Author: Georg Holzmann
Date: Sept 2012

'''

import urllib2
import json
import base64
import getpass


# Auphonic API url
API_URL = "https://auphonic.com/api/"


def get_request(url, username, password):
    """ GET request with HTTP Basic Authentication.
    """
    req = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    req.add_header("Authorization", "Basic %s" % base64string)
    response = urllib2.urlopen(req).read()

    return json.loads(response)


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


def get_soundcloud_uuid(username, password):
    """ Get the UUID of the user's soundcloud account.
    """
    soundcloud_uuid = ""
    url = API_URL + "services.json"
    response = get_request(url, username, password)
    for service in response["data"]:
        if service["type"] == "soundcloud":
            soundcloud_uuid = service["uuid"]

    if not soundcloud_uuid:
        msg = "You have to add your SoundCloud account to Auphonic first!"
        raise RuntimeError(msg)

    return soundcloud_uuid


def get_files(soundcloud_uuid, username, password):
    """ Get all files of the soundcloud account.
    """
    url = API_URL + "service/%s/ls.json" % soundcloud_uuid
    response = get_request(url, username, password)
    return response["data"]


def new_production(input_file, soundcloud_uuid, preset, username, password):
    """ Creates and starts a new production.
    """
    # create the new production
    url = API_URL + "productions.json"
    data = {"service": soundcloud_uuid,
            "input_file": input_file,
            "preset": preset,
            # NOTE: we set the title to the input file name,
            #       because that's the title in SoundCloud!
            "metadata": {"title": input_file},
        }
    response = post_request(url, data, username, password)

    # start the production on Auphonic servers
    production_uuid = response["data"]["uuid"]
    url = API_URL + "production/%s/start.json" % production_uuid
    post_request(url, "", username, password)


def main():
    """ Main function.
    """
    print "\nWelcome to the Auphonic SoundCloud export script!"

    print "\nPlease enter your Auphonic account information:"
    username = raw_input('Auphonic Username: ')
    password = getpass.getpass("Auphonic Password: ")

    # get UUID of the first soundcloud account and all files on the account
    soundcloud_uuid = get_soundcloud_uuid(username, password)
    files = get_files(soundcloud_uuid, username, password)

    print "\nThe following files are on your SoundCloud account:"
    for f in files:
        print "- %s" % f

    print "\nDo you want to process all of them? (y/N)"
    print "ATTENTION: use this function with care and don't spam our system!"
    confirm = raw_input('(y/N): ')
    if confirm != "y":
        return

    print "\nOK, if you are sure, let's make new productions ..."
    print "You need an Auphonic preset to process all files,"
    print "there you can select e.g. the YouTube export."
    print "See https://auphonic.com/engine/presets/ !"
    print
    preset = raw_input('Auphonic Preset UUID: ')

    # create a new production with every file from soundcloud
    print "\nCreating new productions:"
    for f in files:
        print "- %s" % f
        new_production(f, soundcloud_uuid, preset, username, password)

    print "\nFinished!"
    print "Please check your auphonic account or email for status updates!\n"


if __name__ == "__main__":
    main()
