#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Matteo Foglio
"""

import requests, json, sys, string, time, flickrapi, pytz, webbrowser, flickr_datastructures
from getFlickrList import searchInFlickr, searchInFlickrUid
from datetime import datetime, tzinfo
from random import randint
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

key = "6ab5883201c84be19c9ceb0a4f5ba959"
secret = "1d2bcde87f98ed92"
flickrObj = flickrapi.FlickrAPI(key,secret, format = "json")


def read_flickr_IDs(json_filepath):
    all_urls = [] #list of all urls for pics of zebra
    all_ids = [] #list of all ids for pics of zebra
    all_urls, all_ids, total = searchInFlickr(flickrObj, tags = ["grevy's zebra"], text = "grevy's zebra")

    nsid_list = flickr_datastructures.nsid_list(all_ids)
    del all_urls[:]
    del all_ids[:]
    total = 0

    yr = 2010
    while(yr<2019):
        filenameids = 'zebra_ids_' + str(yr)
        filenameurls = 'zebra_urls_' + str(yr)
        fids = open(filenameids, 'w')
        furls = open(filenameurls, 'w')
        min_date = datetime(yr,1,1,0,0,0).strftime("%s")
        max_date = datetime(yr,12,31,11,59,59).strftime("%s")
        for nsid in nsid_list:
            urls,ids,total = searchInFlickrUid(flickrObj, nsid = nsid, tags = ["grevy's zebra"], text = "grevy's zebra", min_taken = min_date, max_taken = max_date)
            #loops through every page to get all the images
            i = 1
            while i*500 < int(total):
                results = searchInFlickrUid(flickrObj, nsid = nsid, tags = ["grevy's zebra"], text = "grevy's zebra", page = i+1, min_taken = min_date, max_taken = max_date)
                urls += results[0]
                ids += results[1]
                i += 1
            #writes each id and url to their respective files each on a new line
            for i in range(0,len(ids)):
                fids.write(ids[i] + "\n")
                furls.write(urls[i] + "\n")
            all_urls += urls
            all_ids += ids
        fids.close()
        furls.close()
        yr += 1

    f1 = open('all_ids','w')
    for i in all_ids:
        f1.write(i + "\n")
    f1.close

    f2 = open('all_urls','w')
    for i in all_urls:
        f2.write(i + "\n")
    f2.close
    print("Total results: ",len(all_ids)," images")
    print(total)
    pass

def clean_flickr_IDs(list_flickr_ID):
    pass

def download_images(list_flickr_ID):
#    urls = []
#    f = open('all_urls','r')


def download_flickr_photo(url, count):
    results_folder = IMG_FOLDER #+ keyword.replace(" ", "_") + "/"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    
    filename = str(count) + ".jpg"

    try:
        #downloads image
        urllib.urlretrieve(url,  results_folder + filename)
        #print 'Downloading image #' + str(count) + ' from url ' + url



#        #Uploads to google drive and then deletes from local machine
#
#        file = drive.CreateFile({'title' : filename, 'parents' : [{'kind' : 'drive#fileLink', 'id' : resultsID}]})
#        file.SetContentFile(filename)
#        file.Upload()
#
#
#        #deletion line
#        os.remove( IMG_FOLDER + filename)

    except Exception as e:
        print str(e) + ' Download failure'
    
    
    pass
