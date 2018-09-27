#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Matteo Foglio
"""

from os import listdir
from os.path import basename, isfile, join, splitext
from wildlife.utils import settings

album_settings =  settings.load_json_settings('album')
album_path =  album_settings['albums_path']

def get_all_album_id():
    """
    :return: integer list of available album id from the album folder
    """
    all_file = [f for f in listdir(album_path) if isfile(join(album_path, f))]
    all_album_id = [int(splitext(basename(file))[0]) for file in all_file]
    return all_album_id

def get_new_id():
    all_album_id = get_all_album_id()
    new_id = max(all_album_id) + 1 if all_album_id else 1
    return new_id

def get_album_path():
    return album_path