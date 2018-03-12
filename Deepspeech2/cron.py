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
import json
import subprocess
import tempfile
import time
import logging
from logging.config import dictConfig
from datetime import datetime
import pydocumentdb.document_client as document_client

# Global settings to be used, change it accordingly
# Name of the docker which has paddlepaddle installed
# Make sure the following docker is pulled from dockerhub
DOCKER_NAME = "dalonlobo/customdeepspeech2"
# Path to be mounted to the docker
MOUNT_PATH = "/mnt/dalon/asr/paddle_ds"
# Path prefix which will be used to mount to docker
PATH_PREFIX = "/Deepspeech"

def updatedb(json_obj, job_collection_link, host, master_key):
    "Updates the cosmos db with the json_obj"
    client = document_client.DocumentClient(host, \
                                        {'masterKey': master_key})
    client.UpsertDocument(job_collection_link, json_obj)

def run_command(command):
    " Run the command in the shell "
    process = subprocess.Popen(command, bufsize=2048, shell=True,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               close_fds=(sys.platform != 'win32'))
    output = process.communicate()
    return process.returncode, output

def run_asr(logger, videoid, videourl):
    """
    Run ASR docker
    """
    if not videourl:
        videourl = "unknown"
    cmd = "sudo nvidia-docker run -v " + MOUNT_PATH + ":" + PATH_PREFIX + \
            " " + DOCKER_NAME + " python " + PATH_PREFIX + "/stt_pipeline.py --videoid "+\
            videoid + " --videourl " + videourl + " --conf_path " + PATH_PREFIX +\
            "/cron_files/config.json"
    logger.debug('Command: ' + cmd)
    return run_command(cmd)

def setup_logging(logs_path):
    """Setting the logging with Timed rotating file handler for the logs
        :input:
            :logs_path: Path where the logs need to be stored
        :output:
            :logger object
    """
    settings_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(name)s:%(levelname)s] ' +\
                            '[%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': logs_path,
                'when': 'midnight',
                'interval': 1
                }
        },
        'loggers': {
            "cron": {
                'handlers': ['file'],
                'level': 'DEBUG'
            },
        }
    }
    dictConfig(settings_dict)
    return logging.getLogger("cron")

def main():
    """
    This code will run the asr for the requests that are queued in cosmos db
    :input:
        --conf_path : path to the configuration file which contains db settings
    :logs: Logs are stored in /tmp
    :Run: python cron.py -c conf.json
    """
    try:
        # Store the logs in temp location
        logs_path = os.path.join(tempfile.gettempdir(), os.path.basename(__file__) + ".logs")
        logger = setup_logging(logs_path)
        # start_time log the start time of the program
        start_time = time.time()
        logger.info("####### Starting the cron program #######")
        parser = argparse.ArgumentParser(description=\
                    "Cron to run the asr for the requests that are queued in cosmos db")
        parser.add_argument('--conf_path', '-c', type=str,
                            help='Path to configuration file')
        args = parser.parse_args()
        # Read the configuration file
        with open(args.conf_path, "r") as opened_file:
            logger.info("Reading the configuration file")
            conf = json.load(opened_file)
            host = conf["HOST"]
            master_key = conf["MASTER_KEY"]
            database_id = conf["DATABASE_ID"]
            ds_job_collection_id = conf["DS_JOB_COLLECTION_ID"]
            database_link = 'dbs/' + database_id
            job_collection_link = database_link + '/colls/' + ds_job_collection_id

        # Get documents from cosmos db
        def get_documents():
            "Select the top 10 requests ordered by priorit and timestamp"
            client = document_client.DocumentClient(host, \
                                              {'masterKey': master_key})
            logger.debug("Reading from db")
            options = {}
            query = "SELECT TOP 10 * FROM " + ds_job_collection_id + \
                    " t WHERE t.status='0' ORDER BY t.priority DESC"
            return list(client.QueryDocuments(job_collection_link, query, options))

        # Process the document
        def process_doc(doc):
            "Process the given document"
            doc["status"] = "1"
            doc["timestamp"] = str(datetime.utcnow().isoformat()[:-3])
            doc["message"] = "Processing request"
            # Update the status to 1
            updatedb(doc, job_collection_link, host, master_key)
            # Run the ASR
            logger.info("Running asr on videoid {}".format(doc["videoid"]))
            exit_code, output = run_asr(logger, doc["videoid"], doc["videourl"])
            logger.debug(output)
            logger.info("run_asr exited with the status code {}".format(exit_code))
            if exit_code != 0:
                # Update the status to -1
                doc["status"] = "-1"
                doc["message"] = "ASR failed"
                updatedb(doc, job_collection_link, host, master_key)
            else:
                # Update the status to 2
                doc["status"] = "2"
                doc["message"] = "Video is transcribed successfully"
                updatedb(doc, job_collection_link, host, master_key)

        documentlist = get_documents()
        while documentlist:
            processing_time = time.time()
            doc = documentlist[0]
            logger.info("Processing video {}".format(doc["videoid"]))
            process_doc(doc)
            logger.info("Processing complete for the video {}".format(doc["videoid"]))
            logger.info("Time taken for video {0}: {1:.2f} Seconds".format(\
                            doc["videoid"], time.time() - processing_time))
            documentlist = get_documents()
        logger.info("Program ran in {0:.2f} Seconds".format(\
                    time.time() - start_time))
        logger.info("####### Exiting program #######")
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt triggered, exiting program graciously")
        sys.exit(0)
    except Exception as general_exception:
        logger.info("!!!! Exception !!!!")
        logger.exception(general_exception)
        sys.exit(-1)

if __name__ == "__main__":
    main()
