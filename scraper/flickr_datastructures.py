'''
    flickr_datastructures.py
    Created by Grae Abbott and Affan Farid
    2018
    
    Notes:
    Album and Set are interchangeable
    User Id and nsid are interchangeable
    
    '''

import requests, json, sys, string, time, flickrapi, pytz, webbrowser
from getFlickrList import searchInFlickr
from datetime import datetime, tzinfo
from classes import Album, Photo
import json
import pickle

key = "6ab5883201c84be19c9ceb0a4f5ba959"
secret = "1d2bcde87f98ed92"

global flickrObj
flickrObj = flickrapi.FlickrAPI(key, secret, format="json")


# pid refers to photo id, nsid is the user id
# stores all ids from the files in one list
def get_ids():
    ids = []
    f = open('all_ids', 'r')
    for line in f:  # each id in the file is stored on a new line
        ids.append(line[:-1])  # stores the id without the newline character at the end
    f.close()
    return ids


def get_urls():
    urls = []
    f = open('all_urls', 'r')
    for line in f:  # each id in the file is stored on a new line
        urls.append(line[:-1])  # stores the id without the newline character at the end
    f.close()
    return urls


# creates list of nsids from photo id list
def nsid_list(ids):
    flickrObj = flickrapi.FlickrAPI(key, secret, format="json")
    nsid_list = []
    for pid in ids:
        photo_info = json.loads(flickrObj.photos.getInfo(photo_id=str(pid)).decode(encoding='utf-8'))
        nsid = photo_info['photo']['owner']['nsid']
        if not nsid in nsid_list:
            nsid_list.append(nsid)
    return nsid_list


# creates user_dict which maps users to a list of their photos that contain grevy's zebras, also writes dict to file to avoid multiple flickr api queries
def create_userdict(ids):
    user_dict = {}
    flickrObj = flickrapi.FlickrAPI(key, secret, format="json")
    for pid in ids:
        photo_info = json.loads(flickrObj.photos.getInfo(photo_id=str(pid)).decode(encoding='utf-8'))
        nsid = photo_info['photo']['owner']['nsid']
        if nsid in user_dict:
            user_dict[nsid].append(pid)
        else:
            user_dict[nsid] = [pid]
    # writes the user_dict to a file to avoid quering the flickr api more than once
    file = open('nsid_dictionary', 'w')
    for i in user_dict.keys():
        file.write(i + "\n")
        file.write(str(user_dict[i]))
        file.write("\n")
    file.close

    return user_dict


# returns a list of nsids(user_ids) given that the user_dict file has been created, and their is no local user_dict
def get_nsids():
    file = open('nsid_dictionary', 'r')
    nsids = []
    count = 0
    for line in file:
        count += 1
        # every other line in the file has an nsid
        if count % 2 == 1:
            nsids.append(line[:-1])
    file.close
    return nsids


# creates a dictionary mapping users to their photos of grevy's if the user dict file has already been created
def get_userdict():
    file = open('nsid_dictionary', 'r')
    user_dict = {}
    count = 0
    nsid = ''
    for line in file:
        count += 1
        if count % 2 == 1:
            nsid = line[:-1]
        else:
            line = line[2:-2]
            user_dict[nsid] = line.split(sep="', '")
    file.close
    return user_dict


def get_album_details(set_id, user):
    # gets list of pictuers in the album

    try: photosets = json.loads(
        flickrObj.photosets.getPhotos(photoset_id=set_id, user_id=user).decode(encoding='utf-8'))
    except:
        time.sleep(5)
        photosets = json.loads(+flickrObj.photosets.getPhotos(photoset_id=set_id, user_id=user).decode(encoding='utf-8'))
    # creates album object we are analyzing and sets the album id, album url, and album name
    newalbum = Album(set_id, user_id=user)
    add_album_url(newalbum)
    albumName = photosets['photoset']['title']
    newalbum.name = albumName

    # initializes minimum and maximum posted/taken time

    """first_posted = json.loads(
        flickrObj.photos.getInfo(photo_id=photosets['photoset']['photo'][0]['id']).decode(
            encoding='utf-8'))['photo']['dates']['posted']
    first_taken = json.loads(
        flickrObj.photos.getInfo(photo_id=photosets['photoset']['photo'][0]['id']).decode(
            encoding='utf-8'))['photo']['dates']['taken']"""
    # converts the text time into unix timestamp
    mint = 1577840461  # 01/01/2020
    maxt = 915152461  # 01/01/1990
    minp = 1577840461
    maxp = 915152461

    # counter in loop which counts number of pictures in album
    album_size = 0
    # number of pictures of species of interest in the album
    num_species = 0
    count1 = 1
    # loops through each picture in the photoset creatingi a photo class object for each image
    if len(photosets['photoset']['photo']) >=500 :
        print(photosets['photoset']["total"])
        count1+=1
    count = 1
    for page in range(0,photosets['photoset']['pages']):
        photosets1 = json.loads(
            flickrObj.photosets.getPhotos(photoset_id=set_id, user_id=user,page = page+1).decode(encoding='utf-8'))
        for j in photosets1['photoset']['photo']:
            start = time.time()
            # print( str(count) + " " + j['id'])
            count += 1
            try:
                photoInfo = json.loads(flickrObj.photos.getInfo(photo_id=j['id']).decode(encoding='utf-8'))
            except:
                time.sleep(10)
                photoInfo = json.loads(flickrObj.photos.getInfo(photo_id=j['id']).decode(encoding='utf-8'))
            if "photo" not in photoInfo:
                continue
            newphoto = Photo(photo_info=photoInfo)
            newphoto.albumId = set_id
            # add_photo_url(newphoto)
            newphoto.url = photoInfo['photo']['urls']['url'][0]['_content']
            newphoto.photo_description = photoInfo['photo']['description']['_content']
            if "location" in photoInfo["photo"]:
                photolocation = photoInfo['photo']['location']
                newphoto.photoLocationX = float(photolocation['latitude'])
                newphoto.photoLocationY = float(photolocation['longitude'])
                newphoto.location = (newphoto.photoLocationX, newphoto.photoLocationY)
            else:
                newphoto.location = 0;

            # add_photo_description(newphoto)
            # add_photo_location(newphoto)

            '''
                NEED TO BE DONE:
                make photo_list a list of photo objects (appending newphoto ) instead of a
                list of photo ids, which it currently is

                see: line 177
                '''

            taken = photoInfo['photo']['dates']['taken']
            # converts the text time into unix timestamp
            taken = datetime.strptime(taken, '%Y-%m-%d %H:%M:%S')
            # print(type(taken))
            taken = int(time.mktime(taken.timetuple()))
            posted = int(photoInfo['photo']['dates']['posted'])
            # posted = int(time.mktime(datetime.strptime(posted, '%Y-%m-%d %H:%M:%S').timetuple()))
            # resets the max/min time if its later/earlier respectively
            if taken < mint:
                mint = taken
            if taken > maxt:
                maxt = taken
            if posted < minp:
                minp = posted
            if posted > maxp:
                maxp = posted
            # adds the photo to the photolist attribute of the album object
            newalbum.photo_list[j['id']] = newphoto

            album_size += 1
            stop = time.time()
            duration = stop - start
            # checks to see if picture has tag of species of interest and updates the count
            # if j['id'] in photolist :
            #    num_species+=1
            newalbum.time_range_posted = int(maxp) - int(minp)
            newalbum.time_range_taken = int(maxt) - int(mint)
            # updates album size
            newalbum.size = album_size
            # calculates species of interest ratio to total number of photos in album
            # newalbum.species_ratio = float(num_species)/float(album_size)

    return newalbum

def create_album_photo_map(albumList):
    temp_dict = {}
    for i in albumList:
        temp_dict[i] = list(albumList[i].photo_list.keys())
    with open('data.json', 'w') as fp:
        json.dump(temp_dict, fp, indent=4)
        # print(type(albumList[i].photo_list))


# creates a list of albums that
def get_albums():
    startTime = time.time()
    # creates flickr object
    flickrObj = flickrapi.FlickrAPI(key, secret, format="json")

    #This is for old albums. Only check albums which were marked good. Can be removed later.
    with open("edited.json", "r") as fp:
        lala = json.load(fp)



    photolist = get_ids()  # list of ids returned from the search on flickr

    albumlist = {}  # {album id: album object}

    # loops through all the photos in the search
    for pid in photolist:

    #for i in range(0, 10):

        #pid = photolist[i]

        all_contexts = json.loads(flickrObj.photos.getAllContexts(photo_id=pid).decode(encoding='utf-8'))
        print(len(all_contexts))
        # list of all set ids
        if 'set' in all_contexts:  # all_contexts["set"] == True
            sets = all_contexts["set"]
            user = \
                json.loads(flickrObj.photos.getInfo(photo_id=pid).decode(encoding='utf-8'))['photo']['owner'][
                    'nsid']
            # loops through all the sets that the photo is in
            filtered_sets = [item.split('/')[-1] for item in lala[pid]]

            for i in sets:
                set_id = i["id"]

                # if the album has not already been processed
                if set_id not in albumlist:
                    if set_id in filtered_sets:
                        newalbum = get_album_details(set_id, user)
                        #print(newalbum.photo_list)
                    else:
                        print(set_id)
                albumlist[newalbum.sid] = newalbum
            #print(albumlist)
        stopTime = time.time()
        duration = stopTime - startTime
    create_album_photo_map(albumlist)
    pickle_out = open("dict33.pickle", "wb")
    pickle.dump(albumlist, pickle_out)
    pickle_out.close()
    return albumlist


def add_album_url(a):
    # constructs the url for each album given album object parameter
    url = "https://www.flickr.com/photos/" + a.user_id + "/albums/" + a.sid
    a.url = url


def add_album_name(a):
    # loads the album name from the api and sets the album object album_name attribute to it
    album_info = json.loads(flickrObj.photosets.getInfo(photoset_id=a.sid, user_id=a.user_id))
    albumUrl = album_info['photoset']['title']['_content']
    a.name = albumUrl


def add_photo_url(p):
    photoInfo = json.loads(flickrObj.photos.getInfo(photo_id=p.id))
    urlString = photoInfo['photo']['urls']['url'][0]['_content']
    p.url = urlString


def add_photo_description(p):
    photodes = json.loads(flickrObj.photos.getInfo(photo_id=p.id).decode(encoding='utf-8'))['photo']['description'][
        '_content']
    p.photo_description = photodes


def add_photo_location(p):
    # error caused by function: KeyError: 'location'
    photolocation = json.loads(flickrObj.photos.getInfo(photo_id=p.id).decode(encoding='utf-8'))['photo']['location']
    p.photoLocationX = float(photolocation['latitude'])
    p.photoLocationY = float(photolocation['longitude'])
    p.location = (p.photoLocationX, p.photoLocationY)
    p.checkIfZoo()


def get_photo_dict(photo_id_list):
    photoDict = {}
    for i in photo_id_list:
        photoDict[i] = {}
        try:
            photoInfo = json.loads(flickrObj.photos.getInfo(photo_id=i).decode(encoding='utf-8'))
        except:
            time.sleep(10)
            photoInfo = json.loads(flickrObj.photos.getInfo(photo_id=i).decode(encoding='utf-8'))
        if "photo" not in photoInfo:
            continue

        photoDict[i]["description"] = photoInfo['photo']['description']['_content']

        if "location" in photoInfo["photo"]:
            photolocation = photoInfo['photo']['location']
            photoLocationX = float(photolocation['latitude'])
            photoLocationY = float(photolocation['longitude'])
            photoDict[i]["location"] = (photoLocationX, photoLocationY)
        else:
            photoDict[i]["location"] = (-1, -1)

        all_contexts = json.loads(flickrObj.photos.getAllContexts(photo_id=i).decode(encoding='utf-8'))
        if 'set' in all_contexts:
            photoDict[i]["albumList"] = {}
            sets = all_contexts["set"]
            user = \
                json.loads(flickrObj.photos.getInfo(photo_id=i).decode(encoding='utf-8'))['photo']['owner'][
                    'nsid']
            for j in sets:

                set_id = j["id"]
                photoDict[i]["albumList"][set_id] = {}
                # if the album has not already been processed
                photosets = json.loads(
                    flickrObj.photosets.getInfo(photoset_id=set_id, user_id=user).decode(encoding='utf-8'))
                photoDict[i]["albumList"][set_id]["name"] = photosets['photoset']['title']['_content']
                photoDict[i]["albumList"][set_id]["description"] = photosets['photoset']['description']['_content']
        taken = photoInfo['photo']['dates']['taken']
        # converts the text time into unix timestamp
        taken = datetime.strptime(taken, '%Y-%m-%d %H:%M:%S')
        # print(type(taken))
        taken = int(time.mktime(taken.timetuple()))
        photoDict[i]["time_taken"] = taken
        photoDict[i]["time_uploaded"] = int(photoInfo['photo']['dates']['posted'])
    return photoDict

def create_json_file(filename):
    with open('dict.pickle', 'rb') as input:
        albumObjDict = pickle.load(input)
    albumDict = {}
    for i in albumObjDict:
        albumDict[albumObjDict[i].sid] = {}
        albumDict[albumObjDict[i].sid]["url"] = albumObjDict[i].url
        albumDict[albumObjDict[i].sid]["user_id"] = albumObjDict[i].user_id
        albumDict[albumObjDict[i].sid]["name"] = albumObjDict[i].name
        albumDict[albumObjDict[i].sid]["size"] = albumObjDict[i].size
        albumDict[albumObjDict[i].sid]["time_range_posted"] = albumObjDict[i].time_range_posted
        albumDict[albumObjDict[i].sid]["time_range_taken"] = albumObjDict[i].time_range_taken
        albumDict[albumObjDict[i].sid]["photo_list"] = []
        for j in albumObjDict[i].photo_list:
            temp_dict = {}
            temp_dict["id"] = albumObjDict[i].photo_list[j].url.split('/')[-2]
            temp_dict["location"] = albumObjDict[i].photo_list[j].location
            temp_dict["time_taken"] = albumObjDict[i].photo_list[j].timeTaken
            temp_dict["time_posted"] = albumObjDict[i].photo_list[j].timePosted
            temp_dict["photographer"] = albumObjDict[i].photo_list[j].photographer
            temp_dict["url"] = albumObjDict[i].photo_list[j].url
            temp_dict["description"] = albumObjDict[i].photo_list[j].photo_description
            albumDict[albumObjDict[i].sid]["photo_list"].append(temp_dict)

    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(albumDict, indent=4))

albumlist = get_albums()

