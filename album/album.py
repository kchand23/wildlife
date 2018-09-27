#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Matteo Foglio
"""

import json
from wildlife.album import manager

class Album:

    """
    The class uses list for its internal implementation because the order of the images could be meaningful.
    """

    def __init__(self, album_id = None, ibeis_url = None):
        """
        Only one (and at least one) between album_id and ibeis_url must be not None.
        :param album_id: if specified, the corresponding album will be loaded, otherwise a new album will be created
        :param ibeis_url: if specied, a new album with be created referring to images on this IBEIS web server
        """

        # only one (and at least one) between album_id and ibeis_url must be not None
        if (album_id is None and ibeis_url is None) or (album_id is not None and ibeis_url is not None):
            raise ValueError("Either set: album_id to load an existing album or set ibeis_url to create a new one")

        # new album
        if album_id is None:
            self.__id = manager.get_new_id()
            self.album = dict()
            self.album['gid_list'] = []
            self.album['ibeis_url'] = ibeis_url
        # load existing album
        else:
            self.__load_album(album_id)

    @classmethod
    def from_id(cls,album_id):
        """
        Load an album from a json file stored in the appropriate album folder.
        :param id: id of the album to be loaded
        :return: properly intialized Album instance with data loaded   
        """
        return cls(album_id,None)

    @classmethod
    def from_scratch(cls,ibeis_url):
        """
        :param ibeis_url: url of the IBEIS web server where the images are stored
        :return: properly initialized Album instance
        """
        return cls(None,ibeis_url)

    def __str__(self):
        return self.get_gid_list().__str__()

    def __repr__(self):
        return self.get_gid_list().__repr__()

    def __get_file_path(self):
        return manager.get_album_path() + str(self.__id) + '.json'

    def __load_album(self, id):
        self.__id = id
        with open(self.__get_file_path(), 'r') as fp:
            self.album = json.load(fp)

    def add(self, gids):
        # add element to gid_list if they are not already in gid_list
        self.album['gid_list'].extend([gid for gid in gids if gid not in self.album['gid_list'] ])

    def remove(self, gids):
        self.album['gid_list'] = [gid for gid in self.album['gid_list'] if gid not in gids]

    def intersect(self, gids):
        self.album['gid_list'] = [gid for gid in self.album['gid_list'] if gid in gids]

    def get_gid_list(self):
        return self.album['gid_list']

    def get_size(self):
        return len(self.album['gid_list'])

    def save_album(self):
        with open(self.__get_file_path(), 'w') as fp:
            json.dump(self.album, fp)

    #TODO
    def extract_features(self):
        raise NotImplementedError


