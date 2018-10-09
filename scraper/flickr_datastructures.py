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

key = "6ab5883201c84be19c9ceb0a4f5ba959"
secret = "1d2bcde87f98ed92"

global flickrObj
flickrObj = flickrapi.FlickrAPI(key,secret, format = "json")

#pid refers to photo id, nsid is the user id
#stores all ids from the files in one list
def get_ids():
    ids = []
    f = open('all_ids','r')
    for line in f: #each id in the file is stored on a new line
        ids.append(line[:-1]) #stores the id without the newline character at the end
    f.close()
    return ids

def get_urls():
    urls = []
    f = open('all_urls','r')
    for line in f: #each id in the file is stored on a new line
        urls.append(line[:-1]) #stores the id without the newline character at the end
    f.close()
    return urls

#creates list of nsids from photo id list
def nsid_list(ids):
    flickrObj = flickrapi.FlickrAPI(key,secret, format = "json")
    nsid_list = []
    for pid in ids:
        photo_info = json.loads(flickrObj.photos.getInfo(photo_id = str(pid)).decode(encoding='utf-8'))
        nsid = photo_info['photo']['owner']['nsid']
        if not nsid in nsid_list:
            nsid_list.append(nsid)
    return nsid_list

#creates user_dict which maps users to a list of their photos that contain grevy's zebras, also writes dict to file to avoid multiple flickr api queries
def create_userdict(ids):
    user_dict = {}
    flickrObj = flickrapi.FlickrAPI(key,secret, format = "json")
    for pid in ids:
        photo_info = json.loads(flickrObj.photos.getInfo(photo_id = str(pid)).decode(encoding='utf-8'))
        nsid = photo_info['photo']['owner']['nsid']
        if nsid in user_dict:
            user_dict[nsid].append(pid)
        else:
            user_dict[nsid] = [pid]
    #writes the user_dict to a file to avoid quering the flickr api more than once
    file = open('nsid_dictionary', 'w')
    for i in user_dict.keys():
        file.write(i + "\n")
        file.write(str(user_dict[i]))
        file.write("\n")
    file.close
    
    return user_dict

#returns a list of nsids(user_ids) given that the user_dict file has been created, and their is no local user_dict
def get_nsids():
    file = open('nsid_dictionary', 'r')
    nsids = []
    count = 0
    for line in file:
        count += 1
        #every other line in the file has an nsid
        if count%2 == 1:
            nsids.append(line[:-1])
    file.close
    return nsids

#creates a dictionary mapping users to their photos of grevy's if the user dict file has already been created
def get_userdict():
    file = open('nsid_dictionary', 'r')
    user_dict = {}
    count = 0
    nsid = ''
    for line in file:
        count += 1
        if count%2 == 1:
            nsid = line[:-1]
        else:
            line = line[2:-2]
            user_dict[nsid] = line.split(sep = "', '")
    file.close
    return user_dict

#creates a list of albums that
def get_albums():
    
    #creates flickr object
    flickrObj = flickrapi.FlickrAPI(key,secret, format = "json")
    photolist = get_ids() #list of ids returned from the search on flickr
    albumlist = {} # {album id: album object}
    
    #loops through all the photos in the search
    for pid in photolist:
        '''
        #for i in range(0,1):
        pid = photolist[i]
        '''
        
        all_contexts = json.loads(flickrObj.photos.getAllContexts(photo_id = pid).decode(encoding='utf-8'))
        
        #list of all set ids
        if 'set' in all_contexts: #all_contexts["set"] == True
            sets = all_contexts["set"]
            
            #loops through all the sets that the photo is in
            for i in sets:
                set_id = i["id"]
                #if the album has not already been processed
                if not(set_id in albumlist):
                    #gets the userid for the owner of the album
                    user = json.loads(flickrObj.photos.getInfo(photo_id = pid).decode(encoding='utf-8'))['photo']['owner']['nsid']
                    #gets list of pictuers in the album
                    photosets = json.loads(flickrObj.photosets.getPhotos(photoset_id = set_id, user_id = user).decode(encoding='utf-8'))
                    #creates album object we are analyzing and sets the album id, album url, and album name
                    newalbum = Album(set_id, user_id = user)
                    add_album_url(newalbum)
                    add_album_name(newalbum)
                    
                    #initializes minimum and maximum posted/taken time
                    first_posted = json.loads(flickrObj.photos.getInfo(photo_id = photosets['photoset']['photo'][0]['id']).decode(encoding='utf-8'))['photo']['dates']['posted']
                    first_taken = json.loads(flickrObj.photos.getInfo(photo_id = photosets['photoset']['photo'][0]['id']).decode(encoding='utf-8'))['photo']['dates']['taken']
                    #converts the text time into unix timestamp
                    mint = int(datetime.strptime(first_taken,'%Y-%m-%d %H:%M:%S').strftime("%s"))
                    maxt = int(datetime.strptime(first_taken,'%Y-%m-%d %H:%M:%S').strftime("%s"))
                    minp = int(first_posted)
                    maxp = int(first_posted)
                    
                    #counter in loop which counts number of pictures in album
                    album_size = 0
                    #number of pictures of species of interest in the album
                    num_species = 0
                    
                    #loops through each picture in the photoset creatingi a photo class object for each image
                    for j in photosets['photoset']['photo']:
                        
                        newphoto = Photo(photoId = j['id'])
                        add_photo_url(newphoto)
                        add_photo_description(newphoto)
                        #add_photo_location(newphoto)
                        
                        '''
                            NEED TO BE DONE:
                            make photo_list a list of photo objects (appending newphoto ) instead of a
                            list of photo ids, which it currently is
                            
                            see: line 177
                            '''
                        taken = json.loads(flickrObj.photos.getInfo(photo_id = j['id']).decode(encoding='utf-8'))['photo']['dates']['taken']
                        #converts the text time into unix timestamp
                        taken = int(datetime.strptime(taken, '%Y-%m-%d %H:%M:%S').strftime("%s"))
                        posted = int(json.loads(flickrObj.photos.getInfo(photo_id = j['id']).decode(encoding='utf-8'))['photo']['dates']['posted'])
                        
                        #resets the max/min time if its later/earlier respectively
                        if taken < mint:
                            mint = taken
                        if taken > maxt:
                            maxt = taken
                        if posted < minp:
                            minp = posted
                        if posted > maxp:
                            maxp = posted
                        #adds the photo to the photolist attribute of the album object
                        newalbum.photo_list.append(j['id'])
                        
                        album_size+=1
                        
                        #checks to see if picture has tag of species of interest and updates the count
                        if j['id'] in photolist :
                            num_species+=1
                
                
                #calculates the time range the album has for taken/posted
                newalbum.time_range_posted = int(maxp) - int(minp)
                newalbum.time_range_taken = int(maxt) - int(mint)
                #updates album size
                newalbum.size = album_size
                #calculates species of interest ratio to total number of photos in album
                newalbum.species_ratio = float(num_species)/float(album_size)
                    
                #adds the album to the albumlist
                albumlist[newalbum.sid] = newalbum

    return albumlist

def add_album_url(a):
    #constructs the url for each album given album object parameter
    url = "https://www.flickr.com/photos/"+a.user_id+"/albums/"+a.sid
    a.url = url

def add_album_name(a):
    #loads the album name from the api and sets the album object album_name attribute to it
    album_name = json.loads(flickrObj.photosets.getInfo(photoset_id = a.sid , user_id = a.user_id).decode(encoding='utf-8'))['photoset']['title']['_content']
    a.name = album_name


def add_photo_url(p):
    photourl = json.loads(flickrObj.photos.getInfo(photo_id = p.id).decode(encoding='utf-8'))['photo']['urls']['url'][0]['_content']
    p.url = photourl


def add_photo_description(p):
    photodes = json.loads(flickrObj.photos.getInfo(photo_id = p.id).decode(encoding='utf-8'))['photo']['description']['_content']
    p.photo_description = photodes

def add_photo_location(p):
    #error caused by function: KeyError: 'location'
    photolocation = json.loads(flickrObj.photos.getInfo(photo_id = p.id).decode(encoding='utf-8'))['photo']['location']
    p.photoLocationX = float(photolocation['latitude'])
    p.photoLocationY = float(photolocation['longitude'])
    p.location = (p.photoLocationX,p.photoLocationY)
    p.checkIfZoo()

