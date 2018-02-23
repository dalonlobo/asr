#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:48:31 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging
import json
import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors

from datetime import datetime

logger = logging.getLogger("__main__")   

class IDisposable:
    """ A context manager to automatically close an object with a close method
    in a with statement. """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None

if __name__ == "__main__":
    """
    Make stt request
    Document definition:
        :videoid: Id of the video to be transcribed
        :videourl: This is an optional field
        :storage_type: This can have 2 values
            "youtube": For youtube videos
            "blob": For videos in blob storage
        :status: This field in the document an have following values
             0: Not processed
             1: Processing
            -1: Failed to create srt
             2: completed
        :priority: Priority at which the request is to be processed
            0: Low
            1: Medium
            2: High
        :timestamp: Time at which added or modified
        :message: Error messages are put here
    Configuration json format:
        {
        "HOST":"https://videokenoffshore.documents.azure.com:443/",
        "MASTER_KEY":"####==",
        "DATABASE_ID":"com.videoken.development.jobqueues",
        "DS_JOB_COLLECTION_ID":"DeepSpeechJobQueueProduction"
        }
    :Run: python request_stt.py --conf_path config.json --priority 0 --storage_type youtube --videoid 123123
    """
    try:
        logs_path = os.path.basename(__file__) + ".logs"
        logging.basicConfig(filename=logs_path,
            filemode='a',
            format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        print("Logs are in ", os.path.abspath(logs_path), file=sys.stderr)
        print("Run the following command to view logs:\n", file=sys.stderr)
        print("tail -f {}".format(os.path.abspath(logs_path)), file=sys.stderr)
        parser = argparse.ArgumentParser(description="mp4 to wav")
        parser.add_argument('--conf_path', type=str,  
                            help='path to configuration file')
        parser.add_argument('--videoid', type=str,  
                            help='videoid to be transcribed')
        parser.add_argument('--storage_type', type=str, default='blob',  
                            help='youtube or blob')
        parser.add_argument('--priority', type=str, default='0',  
                            help='0|1|2 where 0-Low,1-Medium,2-High')
        args = parser.parse_args()
        
        # Read the configuration file
        with open(args.conf_path, "r") as f:
            conf = json.load(f)
            HOST = conf["HOST"]
            MASTER_KEY = conf["MASTER_KEY"]
            DATABASE_ID = conf["DATABASE_ID"]
            DS_JOB_COLLECTION_ID = conf["DS_JOB_COLLECTION_ID"]
            database_link = 'dbs/' + DATABASE_ID
            job_collection_link = database_link + '/colls/' + DS_JOB_COLLECTION_ID
        # Insert into the cosmos db
        def createUpdateDocument(videoid, storage_type, priority, videourl=""):
            # Write into the db
            with IDisposable(document_client.DocumentClient(HOST, \
                                                            {'masterKey': MASTER_KEY})) as client:
                videoJSON = {"videoid": videoid,
                             "videourl": videourl,
                             "storage_type": storage_type,
                             "status": "0",
                             "priority": priority,
                             "timestamp": str(datetime.utcnow().isoformat()[:-3]),
                             "message": ""}
                query = "SELECT * FROM "+DS_JOB_COLLECTION_ID+" t  "+\
                        "WHERE t.videoid = '"+videoid+"'"
                documentlist = list(client.QueryDocuments(job_collection_link, query))
                if len(documentlist):
                    videoJSON["id"] = documentlist[0]["id"]
                    client.UpsertDocument(job_collection_link, videoJSON)
                else:
                    client.CreateDocument(job_collection_link, videoJSON) 
        createUpdateDocument(args.videoid, args.storage_type, args.priority)
        logger.info("#########################")
        logger.info(".....Exiting program.....")
        logger.info("#########################")
        print(".....Exiting program.....", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)