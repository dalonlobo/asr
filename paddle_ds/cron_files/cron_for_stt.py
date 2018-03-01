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
import numpy as np
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
    output = p.communicate()
    logger.debug("Execution completed")
    return p.returncode, output

def run_asr(videoid, videourl):
    """
    Run asr pipeline
    """
    cmd = "sudo nvidia-docker run -v /mnt/dalon/asr/paddle_ds:/Deepspeech dalonlobo/customdeepspeech2 python /Deepspeech/stt_pipeline.py --videoid "+\
            videoid+" --videourl "+videourl+" --conf_path /Deepspeech/cron_files/config.json"
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

if __name__ == "__main__":
    """
    Make stt request
    Document definition:
        :videoid: Id of the video to be transcribed
        :videourl: This is an optional field
        :status: This field in the document an have following values
             0: Not processed
             1: Processing
            -1: Failed to create srt
             2: completed
        :priority: Priority at which the request is to be processed
            0: Low
            1: Medium
            2: High
        :timestamp: Timestamp at which it was created/updated
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
        logs_path = "/tmp/"+os.path.basename(__file__) + ".logs"
        logging.basicConfig(filename=logs_path,
            filemode='a',
            format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        print("Logs are in ", os.path.abspath(logs_path), file=sys.stderr)
        print("Run the following command to view logs:\n", file=sys.stderr)
        print("tail -f {}".format(os.path.abspath(logs_path)), file=sys.stderr)
        logger.info("Starting the cron job")
        parser = argparse.ArgumentParser(description="Cron job setup")
        parser.add_argument('--conf_path', type=str,  
                            help='path to configuration file')
        args = parser.parse_args()
        # Number of requests to process in 1 job
        MAX_DOCUMENTS_TO_PROCESS = 3 
        # Read the configuration file
        with open(args.conf_path, "r") as f:
            conf = json.load(f)
            HOST = conf["HOST"]
            MASTER_KEY = conf["MASTER_KEY"]
            DATABASE_ID = conf["DATABASE_ID"]
            DS_JOB_COLLECTION_ID = conf["DS_JOB_COLLECTION_ID"]
            database_link = 'dbs/' + DATABASE_ID
            job_collection_link = database_link + '/colls/' + DS_JOB_COLLECTION_ID
        
        # Get documents
        def get_documents(priority):
            with IDisposable(document_client.DocumentClient(HOST, \
                                              {'masterKey': MASTER_KEY})) as client:
                logger.debug("Reading from db")
                options = {} 
                query = "SELECT TOP 10 * FROM "+DS_JOB_COLLECTION_ID\
                    +" t WHERE t.status='0' and t.priority='"\
                    +str(priority)+"'"+" ORDER BY t.timestamp ASC"
                return list(client.QueryDocuments(job_collection_link, query, options))
    
        # Process the document
        def process_doc(doc):
            with IDisposable(document_client.DocumentClient(HOST, \
                                                    {'masterKey': MASTER_KEY})) as client:
                videoJSON = {"videoid": doc["videoid"],
                     "videourl": doc["videourl"],
                     "status": "1",
                     "priority": doc["priority"],
                     "timestamp": str(datetime.utcnow().isoformat()[:-3]),
                     "message": "Processing request",
                     "id": doc["id"]}
                # Update the status to 1 
                logger.debug("Processing {}".format(doc["videoid"]))
                updatedb(videoJSON, job_collection_link, HOST, MASTER_KEY)
                try:
                    logger.info("Running asr on".format(doc["videoid"]))
                    exit_code, output = run_asr(doc["videoid"], doc["videourl"])
                    logger.info("run_asr exited with the status code {}".format(exit_code))
                    if exit_code != 0:
                        # Update the status to -1
                        videoJSON["status"] = "-1"
                        videoJSON["message"] = "STT failed"
                        updatedb(videoJSON, job_collection_link, HOST, MASTER_KEY)
                        raise Exception("Error in srt creation")
                    else:
                        # Update the status to 2
                        videoJSON["status"] = "2"
                        videoJSON["message"] = "Video is transcribed successfully"
                        updatedb(videoJSON, job_collection_link, HOST, MASTER_KEY)
                except Exception as e:
                    logger.error("Error while processing:"+doc["videoid"])
                    logger.exception(e)
                    # Update the status to -1
                    videoJSON["status"] = "-1"
                    videoJSON["message"] = "STT failed"
                    updatedb(videoJSON, job_collection_link, HOST, MASTER_KEY)
                    raise Exception("Error in srt creation")
            
        # process random
        def process_random_doc(documentlist):
            # Only 1 document should be processed now to avoid overlap with next cron job
            index_to_process = np.random.randint(0, len(documentlist))
            doc = documentlist[index_to_process]
            process_doc(doc)            
            
        # Read from cosmosdb
        for i in range(MAX_DOCUMENTS_TO_PROCESS):   
            documentlist = get_documents(priority=2)
            if len(documentlist) != 0:
                process_random_doc(documentlist)
                continue
            documentlist = get_documents(priority=1)
            if len(documentlist) != 0:
                process_random_doc(documentlist)
                continue
            documentlist = get_documents(priority=0)
            if len(documentlist) == 0:
                break
            process_random_doc(documentlist)
        logger.info("#########################")
        logger.info(".....Exiting program.....")
        logger.info("#########################")
        print(".....Exiting program.....", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)