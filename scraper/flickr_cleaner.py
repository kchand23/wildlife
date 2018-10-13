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
    for yr in range(2010,2019):
        filenameids = 'zebra_ids_' + str(yr)
        filenameurls = 'zebra_urls_' + str(yr)
        fids = open(filenameids, 'w')
        furls = open(filenameurls, 'w')
        min_date = int(time.mktime(datetime(yr, 1, 1, 0, 0, 0).timetuple()))
        max_date = int(time.mktime(datetime(yr,12,31,11,59,59).timetuple()))
        urls,ids,total = searchInFlickr(flickrObj, text = "grevy's zebra", min_taken = min_date, max_taken = max_date)
        i = len(ids)
        page_num = 2
        while i < int(total):
            results = searchInFlickr(flickrObj, text = "grevy's zebra", page = page_num, min_taken = min_date, max_taken = max_date)
            urls += results[0]
            ids += results[1]
            page_num += 1
            i+=len(results[1])
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
    pass


read_flickr_IDs("try.json")