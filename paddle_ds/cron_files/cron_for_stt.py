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
import subprocess
import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors

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

def updatedb(json, job_collection_link, HOST, MASTER_KEY):
    with IDisposable(document_client.DocumentClient(HOST, \
                                        {'masterKey': MASTER_KEY})) as client: 
        client.UpsertDocument(job_collection_link, json)               

def run_command(command):
    logger.debug("Executing: " + command)
    p = subprocess.Popen(command, bufsize=2048, shell=True, 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         close_fds=(sys.platform != 'win32'))
    logger.debug("Execution completed")
    return p.returncode, output

def run_asr(videoid, storage_type):
    """
    Run asr pipeline
    """
    cmd = "sudo nvidia-docker run -v /mnt/dalon/asr/paddle_ds:/Deepspeech dalonlobo/customdeepspeech2 python /Deepspeech/stt_pipeline.py --videoid "+videoid+" --storage_type "+storage_type
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

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
        :message: Error messages are put here
    Configuration json format:
        {
        "HOST":"https://videokenoffshore.documents.azure.com:443/",
        "MASTER_KEY":"####==",
        "DATABASE_ID":"com.videoken.development.jobqueues",
        "DS_JOB_COLLECTION_ID":"DeepSpeechJobQueueProduction"
        }
    :Run: python cron_for_stt.py --conf_path conf.json
    """
    try:
        logs_path = os.path.basename(__file__) + ".logs"
        logging.basicConfig(filename=logs_path,
            filemode='a',
            format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
            datefmt='%H:%M:%S',
            level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        print("Logs are in ", os.path.abspath(logs_path), file=sys.stderr)
        print("Run the following command to view logs:\n", file=sys.stderr)
        print("tail -f {}".format(os.path.abspath(logs_path)), file=sys.stderr)
        parser = argparse.ArgumentParser(description="mp4 to wav")
        parser.add_argument('--conf_path', type=str,  
                            help='path to configuration file')
        args = parser.parse_args()
        # Number of requests to process in 1 job
        MAX_DOCUMENTS_TO_PROCESS = 2 
        # Read the configuration file
        with open(args.conf_path, "r") as f:
            conf = json.load(f)
            HOST = conf["HOST"]
            MASTER_KEY = conf["MASTER_KEY"]
            DATABASE_ID = conf["DATABASE_ID"]
            DS_JOB_COLLECTION_ID = conf["DS_JOB_COLLECTION_ID"]
            database_link = 'dbs/' + DATABASE_ID
            job_collection_link = database_link + '/colls/' + DS_JOB_COLLECTION_ID
        
        # Read from cosmosdb
        for i in range(MAX_DOCUMENTS_TO_PROCESS):
            with IDisposable(document_client.DocumentClient(HOST, \
                                                    {'masterKey': MASTER_KEY})) as client:   
                logger.debug("Reading from db")
                options = {} 
                options['maxItemCount'] = 1
                query = "SELECT * FROM "+DS_JOB_COLLECTION_ID+" t WHERE t.status='0'"
                documentlist = client.QueryDocuments(job_collection_link, query, options)
                for doc in documentlist:
                    videoJSON = {"videoid": doc["videoid"],
                                 "videourl": doc["videourl"],
                                 "storage_type": doc["storage_type"],
                                 "status": "1",
                                 "message": "Processing request",
                                 "id": doc["id"]}
                    # Update the status to 1 
                    logger.debug("Processing {}".format(doc["videoid"]))
                    updatedb(videoJSON, job_collection_link, HOST, MASTER_KEY)
                    try:
                        logger.info("Running asr on".format(doc["videoid"]))
                        exit_code, output = run_asr(doc["videoid"], doc["storage_type"])
                        logger.info("run_asr exited with the status code {}".format(exit_code))
                        if exit_code != 0:
                            # Update the status to -1
                            videoJSON["status"] = "-1"
                            videoJSON["message"] = "ASR creating failed"
                            updatedb(videoJSON, job_collection_link, HOST, MASTER_KEY)
                            raise Exception("Error in srt creation")
                        else:
                            # Update the status to 2
                            videoJSON["status"] = "2"
                            videoJSON["message"] = "Video is transcribed successfully"
                            updatedb(videoJSON, job_collection_link, HOST, MASTER_KEY)
                    except Exception as e:
                        logger.exception(e)
                        # Update the status to -1
                        videoJSON["status"] = "-1"
                        videoJSON["message"] = "ASR creating failed"
                        updatedb(videoJSON, job_collection_link, HOST, MASTER_KEY)
                        raise Exception("Error in srt creation")
        logger.info("#########################")
        logger.info(".....Exiting program.....")
        logger.info("#########################")
        print(".....Exiting program.....", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)