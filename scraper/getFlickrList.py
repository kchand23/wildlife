#!/bin/python3
# Author: Lorenzo Semeria


import flickrapi as f
from urllib.request import urlretrieve
from functools import partial
from multiprocessing.pool import Pool
import os, re, json, time

import http.client, urllib.request, urllib.parse
from xml.dom import minidom
from datetime import datetime
import sys
key = "6ab5883201c84be19c9ceb0a4f5ba959"
secret = "1d2bcde87f98ed92"
global apiInstance
# From AnimalWildlifeEstimator "SocialMediaImageExtracts

def searchInFlickr(flickrObj, tags=[], text=None, page=1, min_taken=1262304000, max_taken=int(datetime.now().timestamp())):
    photosJson = json.loads(flickrObj.photos.search(tags=tags, text=text, privacy_filter=1, page=page, per_page=500,
                                                    min_taken_date=min_taken,max_taken_date=max_taken, sort = 'relevance').decode(encoding='utf-8'))
    total = photosJson['photos']['total']
    photos = photosJson['photos']['photo']
    urlList = []
    photoID = []
    for i in range(len(photos)):
        dct = photos[i]
        url = 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % (
        str(dct['farm']), dct['server'], dct['id'], dct['secret'])
        photoID.append(dct['id'])
        urlList.append(url)

    return urlList, photoID, total

#searches a certain users flickr photostream given their nsid
def searchInFlickrUid(flickrObj,nsid, tags=[], text=None, page=1, min_taken=1262304000, max_taken=int(datetime.now().timestamp())):
    photosJson = json.loads(flickrObj.photos.search(tags=tags, text=text, user_id = nsid, privacy_filter=1, page=page, per_page=500,
                                                    min_taken_date=min_taken,max_taken_date=max_taken, sort = 'relevance').decode(encoding='utf-8'))
    total = photosJson['photos']['total']
    photos = photosJson['photos']['photo']
    urlList = []
    photoID = []
    for i in range(len(photos)):
        dct = photos[i]
        url = 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % (
        str(dct['farm']), dct['server'], dct['id'], dct['secret'])
        photoID.append(dct['id'])
        urlList.append(url)

    return urlList, photoID, total

def scrape_flickr(to_page, out_fl_nm, query=[], config_file="WebScrapeConfig.xml",min_taken=-1,max_taken=-1):
    global apiInstance
    urlListMaster = []
    oldUrlListLen = 0
    days = 0
    while min_taken < max_taken:

        curMax = min_taken + 86400 # ONE DAY

        try:

            for i in range(1, to_page):

                urlList, photoIDList = searchInFlickr(apiInstance, tags=query, text=None, page=i, min_taken=min_taken, max_taken=curMax)
                urlListMaster.extend(urlList)
                if len(urlListMaster) == oldUrlListLen:
                    break
                else:
                    oldUrlListLen = len(urlListMaster)
        except KeyboardInterrupt:
            print('Wrapping up!')
            break
        except Exception as e:
            print('Exception', e)
        min_taken = curMax
        days += 1
        #print('scrape', out_fl_nm, 'is at', oldUrlListLen, 'day', days)
    print('scrape', out_fl_nm, 'done, found', oldUrlListLen, 'imgs, days', days)
    urlListMaster = list(set(urlListMaster))
    urlListMaster = list(map(lambda x: x.split('/')[-1], urlListMaster))
    with open(out_fl_nm, "w") as urlListFl:
        for url in urlListMaster:
            urlListFl.write(url + "\n")


def main():
    global apiInstance
    apiInstance = f.FlickrAPI(flickrKey, flickrSec, format='json')
    start = datetime.now()
    pages = 100 #int(sys.argv[1])

    queries = ["grevy's zebra"]
    years = range(2010, 2018) # NO 2018 included!!!!

    for name in queries:
        for y in years:
            min_taken_year = y #int(sys.argv[2])
            max_taken_year = min_taken_year+1
            min_taken = int(datetime.strptime(str(min_taken_year), '%Y').timestamp()) # 01/01/YYYY 00:00 local tz
            max_taken = datetime.strptime(str(max_taken_year), '%Y') # 01/01/YYYY+1 00:00 local tz
            max_taken = int(datetime.fromtimestamp(max_taken.timestamp()-1).timestamp()) # 31/12/YYYY 23:59 local tz
            scrape_flickr(pages,'files\\' + str(name)+str(min_taken_year)+'.txt',[str(name)],min_taken=min_taken, max_taken=max_taken)
    print('Start', start.ctime())
    print('End', datetime.now().ctime())
if __name__ == '__main__':
    main()






