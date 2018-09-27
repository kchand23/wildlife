# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 15:22:52 2018

@author: Matteo Foglio
"""

import requests
import time
import json


class WildbookAPI:
    """
        - AID is a unique identifier for an annotation (i.e. a bbox containing an animal)
        - CID is a unique identifier for a contributor (i.e. a photographer)
        - GID is a unique identifier for a photo
        - NID is a unique identifier for an exemplar

        Note: a single NID could correspond to multiple AID (i.e. same animals in different images)
    """

    def __init__(self, domain, read_only=True, verbose=False):
        # remove backslash at the end of the domain
        while domain.endswith('/'):
            domain = domain[:-1]
        self.domain = domain
        self.read_only = read_only
        self.verbose = verbose

    def __request__(self, method, api, data_dict={}):
        url = self.domain + api
        if method == 'get':
            response = requests.get(url, data=data_dict)
        else:
            self.__stop_if_read_only()
            if method == 'post':
                response = requests.post(url, json=data_dict)
            elif method == 'post_files':
                response = requests.post(url, files=data_dict)
            elif method == 'put':
                response = requests.put(url, data=data_dict)
            elif method == 'delete':
                response = requests.delete(url, data=data_dict)
            else:
                raise ValueError

        response_dict = response.json()

        if self.verbose:
            print(response_dict)

        try:
            assert response.ok
        except AssertionError:
            message = response_dict['status']['message']
            print('!!! FAILED REQUEST !!!')
            print('\t URL      = %r' % url)
            print('\t DATA   = %r' % data_dict)
            print('\n%s\n....' % str(response_dict)[:2000])
            #print('\t METHOD   = %r' % method.__name__)
            print('\t RESPONSE = %s\n\n' % message)

        assert response_dict['status']['success']
        return response_dict['response']

    def __stop_if_read_only(self):
        if self.read_only:
            raise PermissionError("Set read_only = True when initializing the class")

    # DELETE REQUESTS

    def delete_aid(self, aid_list):
        """
        Delete corresponding annotations
        :param aid_list:
        :return:
        """
        self.__stop_if_read_only
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('delete', '/api/annot/', data_dict)

    def delete_gid(self, gid_list):
        """
        Delete corresponding image
        :param gid_list:
        :return:
        """
        data_dict = {'gid_list': str(gid_list)}
        return self.__request__('delete', '/api/image/', data_dict)

    def delete_name(self, aid_list):
        return self.set_name(aid_list, ['____'] * len(aid_list))

    def delete_nid(self, nid_list):
        data_dict = {'name_rowid_list': str(nid_list)}
        return self.__request__('delete', '/api/name/', data_dict)

    # GET REQUESTS

    def get_all_aids(self):
        return self.__request__('get', '/api/annot/')

    def get_all_cids(self):
        # workaround: return self.__request__('get', '/api/contributor/') not working
        all_gid_list = self.get_all_gids()
        all_cid_list = list(set(self.get_cid_of_gid(all_gid_list)))
        return all_cid_list

    def get_all_gids(self):
        return self.__request__('get', '/api/image/')

    def get_all_nids(self):
        return self.__request__('get', '/api/name/')

    def get_all_species(self):
        aid_list = self.get_all_aids()
        species_list = self.get_species_of_aid(aid_list)
        return list(set(species_list))

    def get_aid_of_gid(self, gid_list):
        data_dict = {'gid_list': str(gid_list)}
        return self.__request__('get', '/api/image/annot/rowid/', data_dict)

    def get_aid_of_nid(self, nid_list):
        data_dict = {'nid_list': str(nid_list)}
        return self.__request__('get', '/api/name/annot/rowid/', data_dict)

    def get_bbox_of_aid(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/bbox/', data_dict)

    def get_confidence_of_aid(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/detect/confidence/', data_dict)

    def get_cid_of_gid(self, gid_list):
        data_dict = {'gid_list': str(gid_list)}
        return self.__request__('get', '/api/image/contributor/rowid/', data_dict)

    def get_uuid_of_aid(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/uuid/', data_dict)

    def get_exemplar_of_aid(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/exemplar/', data_dict)

    def get_geolocation_of_gid(self, gid_list):
        data_dict = {'gid_list': str(gid_list)}
        return self.__request__('get', '/api/image/gps/', data_dict)

    def get_gid_of_aid(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/image/rowid/', data_dict)

    def get_gid_of_cid(self, cid_list):
        data_dict = {'contributor_rowid_list': str(cid_list)}
        return self.__request__('get', '/api/contributor/image/rowid/', data_dict)

    def get_gid_of_nid(self, nid_list):
        data_dict = {'nid_list': str(nid_list)}
        return self.__request__('get', '/api/name/image/rowid/', data_dict)

    def get_job(self, job_id):
        data_dict = {'jobid': job_id}
        return self.__request__('get', '/api/engine/job/result/', data_dict)

    def get_name_of_aid(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/name/text/', data_dict)

    def get_nid_of_aid(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/name/rowid/', data_dict)

    def get_species_of_aid(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/species/', data_dict)

    def get_theta(self, aid_list):
        data_dict = {'aid_list': str(aid_list)}
        return self.__request__('get', '/api/annot/theta/', data_dict)

    def get_uuid_of_gid(self, gid_list):
        data_dict = {'gid_list': str(gid_list)}
        return self.__request__('get', '/api/image/uuid/', data_dict)

    def get_image_url(self, gid_list):
        """
        :param gid: gid of the requested image
        :return: a public url pointing to the image
        """
        return [self.domain + '/api/image/src/%s/' % str(gid) for gid in gid_list]

    # PUT REQUEST

    def set_cid(self, gid_list, contributor_list):
        data_dict = {
            'gid_list': str(gid_list),
            'contributor_rowid_list': str(contributor_list)}
        return self.__request__('put', '/api/image/contributor/rowid/', data_dict)

    def set_geolocation(self, gid_list, gps_list):
        """
        :param gps_list: list of list where inner lists contain gps coordinates
        """
        data_dict = {
            'gid_list': str(gid_list),
            'gps_list': str(gps_list)}
        return self.__request__('put', '/api/image/gps/', data_dict)

    def set_name(self, aid_list, name_list):
        data_dict = {
            "aid_list": json.dumps(aid_list),
            "name_list": json.dumps(name_list)
        }
        return self.__request__('put', '/api/annot/name/', data_dict)

    def set_species(self, aid_list, species_list):
        data_dict = {
            'aid_list': str(aid_list),
            'species_text_list': str(species_list)}
        return self.__request__('put', '/api/annot/species/', data_dict)

    # ADVANCED 

    def get_aid_of_species(self, requested_species_list):
        # check that the species name is valid and present on the server
        valid_species = self.get_all_species()
        try:
            assert all([species in valid_species for species in requested_species_list])
        except AssertionError:
            print('Species not valid (or not present among the photos on the server)')
            print('Are you sure you are providing a LIST of species?')

        aid_list = self.get_all_aids()
        species_list = self.get_species_of_aid(aid_list)
        requested_aids = [aid for aid, species in zip(aid_list, species_list) if species in requested_species_list]
        return requested_aids

    def get_aid_of_uuid(self, requested_uuid_list):
        """
        Note: usually uuid are provided as a list of dict of type {'__UUID__': '...........'}
        :param requested_uuid_list: a list of uuid as a list of string (not as a list of dict)
        :return:
        """
        all_aid_list = self.get_all_aids()
        all_uuid_list = [value for dict in self.get_uuid_of_aid(all_aid_list) for value in dict.values()]
        requested_aid_list = [aid for aid, uuid in zip(all_aid_list, all_uuid_list) if uuid in requested_uuid_list]
        return requested_aid_list

    def get_gid_by_species(self, species_list):
        aid_list = self.get_aid_of_species(species_list)
        gid_list = self.get_gid_of_aid(aid_list)
        return list(set(gid_list))

    def get_gid_list_with_low_confidence(self, confidence_threshold, species_list=None):
        """ Returns all the aid for which the confidence is lower than the
            given threshold
        """
        aid_list = []
        if species_list:
            aid_list = self.get_aid_of_species(species_list)
        else:
            aid_list = self.get_all_aids()

        confidence_list = self.get_confidence_of_aid(aid_list)
        low_confidence_aid = [aid for aid, conf in zip(aid_list, confidence_list) if conf < confidence_threshold]
        low_confidence_gid = self.get_gid_of_aid(low_confidence_aid)
        return low_confidence_gid

    def wait_for_job_completion(self, job_id, sleep_time=0.5):
        job_status = 'invalid'
        while (job_status == 'invalid'):
            time.sleep(sleep_time)
            job_status = self.get_job(job_id)['status']
        assert (job_status == 'ok'), 'job %s terminate with status %s' % (job_id, job_status)

    def get_gid_list_with_no_annotations(self):
        """ 
        Run the detect on all the image with no annotations
        NOTE: an image may have no animals and therefore will never have annotations!
        """
        gid_list = self.get_all_gids()
        # generate a list of True/False values
        has_no_annotation = [len(x) == 0 for x in self.get_aid_of_gid(gid_list)]
        gids_with_no_annotations = [gid for gid, cond in zip(gid_list, has_no_annotation) if cond == True]
        return gids_with_no_annotations

    # UPLOAD

    def upload_image(self, image_path):
        """
        :param image_path: file path of the image to be uploaded
        :return: a list of gid of the uploaded image
        """
        data_dict = ()
        with open(image_path, 'rb') as fp:
            data_dict = {'image': fp.read()}
        return self.__request__('post_files', '/api/upload/image/', data_dict)

    # DETECTION

    def __detect(self, image_uuid_list):
        data_dict = {'image_uuid_list': image_uuid_list}
        # Detection with engine (i.e. non-blocking)
        job_id = self.__request__('post', '/api/engine/detect/cnn/yolo/', data_dict)
        # Detection without engine (i.e. blocking --> do not use it!)
        # return self.__request__('post','/api/detect/cnn/yolo/json/',data_dict)
        return job_id

    """def draw_boxes_on_thumbnails(self, job_id_list):
        ""
        Before calling this function you must run the detection and wait for 
        their completion.
        This function draw boxes around the animals detected so that results
        can be easier checked on the web interface.
        ""
        aid_lists = []
        for job_id in job_id_list:
            # extract information about each aid from results
            detections_list = self.get_job(job_id)['json_result']['results_list'][0]
            # add annotations based on detection results
            gid_list = [gid] * len(detection_list)
            bbox_list = [(detection['xtl'],detection['ytl'],detection['width'],detection['height']) for detection in detection_list]
            theta_list = [detection['theta'] for detection in detection_list]
            species_list = [detection['class'] for detection in detection_list]
            confidence_list = [detection['confidence'] for detection in detection_list]
            data_dict = {
                'gid_list': gid_list,
                'bbox_list': bbox_list,
                'theta_list': theta_list,
                'species_list': species_list,
                'confidence_list': confidence_list,
            }
            aid_list = self.__request__('post', '/api/annot/', data_dict)
            aid_lists.append(aid_list)
        return aid_lists"""

    """def draw_boxes_on_thumbnails(self):
        ""
        Before calling this function you must run the detection and wait for 
        their completion.
        This function draw boxes around the animals detected so that results
        can be easier checked on the web interface.
        ""
        aid_list = self.get_all_aids()
        bbox_list = [(x[0],x[1],x[2],x[3]) for x in self.get_bbox_of_aid(aid_list)]
        #theta_list = self.get_theta(aid_list)
        #species_list = self.get_species(aid_list)
        #confidence_list = self.get_confidence(aid_list)
        
        data_dict = {
                'gid_list': gid_list,
                'bbox_list': bbox_list,
         #       'theta_list': theta_list,
         #       'species_list': species_list,
         #       'confidence_list': confidence_list,
            }
        
        aid_list = self.__request__('post', '/api/annot/', data_dict)

        return data_dict"""

    def run_complete_detection_pipeline(self, fast=True, start_from_gid=0, group_size=12):
        """
        :param fast: if enabled, the detection will be run only on images with 
                    zero animals detected (i.e. images with no annotations).
                    Otherwise the detection will be run on all the images
        :param start_from_gid: all gid <= start_from_gid will be skipped
        :param group_size: set the number of jobs to sent to the server (to
                    parallelize tasks)
        """
        # get gids with no annotation
        gids = self.get_gid_list_with_no_annotations() if fast else self.get_all_gids()
        # remove first gid according to parameter
        gids = [x for x in gids if x >= start_from_gid]
        # create groups
        gid_groups = [gids[i:i + group_size] for i in range(0, len(gids), group_size)]
        # perform detection
        for gid_list in gid_groups:
            print('gid %s ' % str(gid_list), end='')
            time_start = time.time()
            uuid_list = self.get_uuid_of_gid(gid_list)
            job_id = self.__detect(uuid_list)
            self.wait_for_job_completion(job_id, sleep_time=1)
            print(' | job-id %s | ' % job_id, end='')
            print(' --> completed in %f seconds' % (time.time() - time_start))
        # update thumbnails with the result
        # self.draw_boxes_on_thumbnails(job_id_list)

    # IDENTIFICATION

    def __get_suitable_nid(self, aid_list):
        """
        :param aid_list: aid of the same exemplar for which we want to assign a nid
        :return: if one of the aid in aid_list has a nid, returns that nid
                if none of the aid in aid_list has a nid, returns a new suitable nid (by taking the last and adding 1)
        """
        nid_list = self.get_nid_of_aid(aid_list)

        # check if any aid has an nid (note that an aid has no nid if the nid returned from the server is negative)
        nid_positive_list = [nid for nid in nid_list if nid > 0]
        if nid_positive_list:  # at least one aid has an nid
            nid_requested = nid_positive_list[0]
        else:  # no aid has an nid
            all_existing_nid = self.get_all_nids()
            if not all_existing_nid:  # the server has no nid: first animal ever identified on the server
                nid_requested = 1
            else:
                nid_requested = all_existing_nid[-1] + 1
        return nid_requested

    def __aid_from_identification_results(self, job_id, match_threshold):
        # get job result
        job_result = self.get_job(job_id)['json_result']

        # extract the uuid list of the aid matched
        uuid_requested = job_result['query_annot_uuid_list'][0]['__UUID__']
        uuid_matched_pair_list = job_result['inference_dict']['annot_pair_dict']['review_pair_list']

        # filter the uuid matched by the threshold
        uuid_matched_list = []
        for uuid_matched_pair in uuid_matched_pair_list:
            if (uuid_matched_pair['annot_uuid_1']['__UUID__'] == uuid_requested):
                uuid_matched = uuid_matched_pair['annot_uuid_2']['__UUID__']
                p_match = uuid_matched_pair['prior_matching_state']['p_match']
                p_nomatch = uuid_matched_pair['prior_matching_state']['p_nomatch']
                print(" p_match %f | p_nomatch %f" % (p_match, p_nomatch))
                if (p_match >= match_threshold):
                    uuid_matched_list.append(uuid_matched)

        # extract the uuid-aid correspondence
        # note: it cannot be extracted from job_result because it contains a mixture of nid and negative aid (when
        # the annotation hasn't already been matched to an nid
        query_uuid_list = [uuid_requested]
        query_uuid_list.extend(uuid_matched_list)
        query_aid_list = self.get_aid_of_uuid(query_uuid_list)
        map_uuid_to_aid = dict(zip(query_uuid_list, query_aid_list))

        # create list of matched aid
        aid_matched_list = list()
        # add the requested aid
        aid_matched_list.append(map_uuid_to_aid[uuid_requested])
        # add the other aid (the ones filtered based on the threshold!)
        aid_matched_list.extend([map_uuid_to_aid[uuid] for uuid in uuid_matched_list])

        return aid_matched_list

    def __run_single_annot_identification(self, aid, aid_against_list, match_threshold):
        """
        :param aid: aid to be identified
        :param aid_against_list: aid list to be checked against the given aid
        """
        # retrieve uuid
        uuid = self.get_uuid_of_aid([aid])
        uuid_against_list = self.get_uuid_of_aid(aid_against_list)
        # run the detection against all the available annots 
        data_dict = {
            'query_annot_uuid_list': uuid,
            'database_annot_uuid_list': uuid_against_list
        }
        job_id = self.__request__('post', '/api/engine/query/graph/', data_dict)
        print(job_id)
        # wait for job completion
        self.wait_for_job_completion(job_id)
        # get results
        aid_matched_list = self.__aid_from_identification_results(job_id, match_threshold)
        # find a suitable name for the animals
        nid = self.__get_suitable_nid(aid_matched_list)
        # assign the name to all the aids matched
        self.set_name(aid_matched_list, [str(nid)] * len(aid_matched_list))

    def run_complete_identification_pipeline(self, gid_list, species, match_threshold):
        """
        :param gid_list:
        :param species:
        :param match_threshold: a matching will be skipped if the probability of the matching is lower than match_threshold
            - suggested threshold for zebra_plains: 0.8
        :return:
        """
        # get aids for all gid
        aid_list = [x for y in self.get_aid_of_gid(gid_list) for x in y]  # flatten the list

        name_list = []
        for aid_sublist in self.__split_list(aid_list, 10 ** 3):
            name_list.extend(self.get_name_of_aid(aid_sublist))
        name_dict = {aid_list[i]: name_list[i] for i in range(len(aid_list))}

        species_list = []
        for aid_sublist in self.__split_list(aid_list, 10 ** 3):
            species_list.extend(self.get_species_of_aid(aid_sublist))
        species_dict = {aid_list[i]: species_list[i] for i in range(len(aid_list))}

        # limit matching to only <species>
        all_aid_list_species_only = [aid for aid in aid_list if species_dict[aid] == species]
        all_aid_list_species_only.reverse()

        # retrieve all exemplars and perform identification only against them?
        # requires more client-side management: In fact:
        #   1. how can we now that all the images have already been processed?
        #   2. what if there are some images that have no exemplar?

        for aid in all_aid_list_species_only:
            # ignore the annotation if it has already an nid associated (i.e. they has already been identified)
            nid = self.get_nid_of_aid([aid])[0]
            if nid < 0:  # it doesn't have an nid
                aid_against_list = all_aid_list_species_only.copy()
                aid_against_list.remove(aid)
                print("\nRunning ID detection of aid %s against %d annotations" % (aid, len(aid_against_list)))
                self.__run_single_annot_identification(aid, aid_against_list, match_threshold)

    def delete_all_identification_data(self):
        """
        Requires confirmation from console to proceed.
        :return:
        """
        is_sure = input('Are you sure? [yes/no]')
        if(is_sure == 'yes' or is_sure=='y'):
            print("Deleting data...")
            all_aid_list = self.get_all_aids()
            self.delete_name(all_aid_list)
            self.delete_nid(all_aid_list)

    # utils
    def __split_list(self, my_list, sublist_max_size):
        return [my_list[i:i + sublist_max_size] for i in range(0, len(my_list), sublist_max_size)]
