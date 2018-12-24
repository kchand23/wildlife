import json
import pickle
import json
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

with open("albumDict.json") as fp:
    albumDict = json.load(fp)

with open("album_classification.json","r") as fp1:
    filtered_dict = json.load(fp1)

def get_ids():
    ids = []
    f = open('all_ids', 'r')
    for line in f:  # each id in the file is stored on a new line
        ids.append(line[:-1])  # stores the id without the newline character at the end
    f.close()
    return ids



def add_album_url(a):
    # constructs the url for each album given album object parameter
    url = "https://www.flickr.com/photos/" + a.user_id + "/albums/" + a.sid
    a.url = url

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
    with open('data1.json', 'w') as fp:
        json.dump(temp_dict, fp, indent=4)
        # print(type(albumList[i].photo_list))




albumlist = {}

for i in filtered_dict:
    if filtered_dict[i] == "yes":
        if i in albumDict:
            if len(albumDict[i]['photo_list']) >= 500:
                print(i)
                if i not in albumlist:
                    newalbum = get_album_details(i, albumDict[i]['user_id'])
                    albumlist[newalbum.sid] = newalbum
                    print(len(newalbum.photo_list))

                    create_album_photo_map(albumlist)
                    pickle_out = open("dict1.pickle", "wb")
                    pickle.dump(albumlist, pickle_out)
                    pickle_out.close()


# create_album_photo_map(albumlist)
# pickle_out = open("dict1.pickle", "wb")
# pickle.dump(albumlist, pickle_out)
# pickle_out.close()