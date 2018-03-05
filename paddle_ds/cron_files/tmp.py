#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 15:49:46 2018

@author: dalonlobo

Document: http://azure.github.io/azure-documentdb-python/
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
import json
import numpy as np
"""
Following are the definitions of the document fields:
videoid: Id of the video to be transcribed
videourl: This is an optional field
storage_type: This can have 2 values
    "youtube": For youtube videos
    "blob": For videos in blob storage
status: This field in the document an have following values
     0: Not processed
     1: Processing
    -1: Failed to create srt
     2: completed
"""

with open("config.json", "r") as f:
    conf = json.load(f)
    HOST = conf["HOST"]
    MASTER_KEY = conf["MASTER_KEY"]
    DATABASE_ID = conf["DATABASE_ID"]
    DS_JOB_COLLECTION_ID = conf["DS_JOB_COLLECTION_ID"]
    database_link = 'dbs/' + DATABASE_ID
    job_collection_link = database_link + '/colls/' + DS_JOB_COLLECTION_ID

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

def createNewDocument(videoid):
    # Write into the db
    with IDisposable(document_client.DocumentClient(HOST, \
                                                    {'masterKey': MASTER_KEY})) as client:
        videoJSON = {"videoid": videoid,
                     "videourl": "",
                     "storage_type": "blob",
                     "status": "0",
                     "message": ""}
        client.CreateDocument(job_collection_link, videoJSON, options=options) 


#def updateDocument(videoid):
#    # Write into the db
#    with IDisposable(document_client.DocumentClient(HOST, \
#                                                    {'masterKey': MASTER_KEY})) as client:
#        videoJSON = {"videoid": videoid,
#                     "videourl": "",
#                     "storage_type": "blob",
#                     "status": "0",
#                     "message": ""} 
#        videoJSON = {"status": "1", "id": "d45cef30-6805-400c-93b4-4ba9377f7f58"}
#        client.UpsertDocument(job_collection_link, videoJSON)

        
createNewDocument("test1")
#updateDocument("test1")

#client.QueryDocuments(job_collection_link, query_with_optional_parameters)



options = {} 
options['maxItemCount'] = 2
query = """SELECT * FROM DeepSpeechJobQueueProduction t
            WHERE t.videoid='3WX7bweJK-k'"""
documentlist = client.QueryDocuments(job_collection_link, query, options)
for doc in documentlist:
    print(doc["videoid"],doc["status"],doc["message"])
    


def get_priority(status,priority):
    with IDisposable(document_client.DocumentClient(HOST, \
                                                    {'masterKey': MASTER_KEY})) as client:   
        options = {} 
        query = "SELECT * FROM "+DS_JOB_COLLECTION_ID+" t WHERE t.status!='"+str(status)+"'"+" and t.priority='"+str(priority)+"'"
        documentlist = list(client.QueryDocuments(job_collection_link, query, options))
        for doc in documentlist:
            print(doc["videoid"],doc["status"],doc["message"], doc["priority"], doc["timestamp"])
    

# Command to insert into db
#/home/dalonlobo/workspace/ppevenv/bin/ppevenv/ds/bin/python /home/dalonlobo/deepspeech_models/asr/paddle_ds/cron_files/request_stt.py --conf_path /home/dalonlobo/deepspeech_models/asr/paddle_ds/cron_files/config.json --storage_type blob --videoid y8j1HL5QCjA

# Read from the db
with IDisposable(document_client.DocumentClient(HOST, \
                                                {'masterKey': MASTER_KEY})) as client:    
    documentlist = client.ReadDocuments(job_collection_link)
    for doc in documentlist:
        print(doc["videoid"],doc["status"],doc["message"], doc["priority"], doc["timestamp"])

# Use this very carefully
############### Danger####################        
with IDisposable(document_client.DocumentClient(HOST, \
                                                {'masterKey': MASTER_KEY})) as client:    
    documentlist = client.ReadDocuments(job_collection_link)
    options = {} 
    options['enableCrossPartitionQuery'] = True
    for doc in documentlist:
        print(doc)
        print(doc["_self"])
#        options['partitionKey'] = True
        client.DeleteDocument(doc["_self"], options=options)
############ Till Here #####################

import sys
import subprocess

def run_command(command):
    p = subprocess.Popen(command, bufsize=2048, shell=True, 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         close_fds=(sys.platform != 'win32'))
    output = p.communicate()
    return p.returncode, output

# to make a request
for v in x:
    p=str(np.random.randint(0,3))
    cmd = '''curl -i -H "Content-Type: application/json" -X POST -d '{"video_id":"'''+v+'''","url":"https://www.youtube.com/watch?v='''+v+'''","priority":"'''+p+'''"}' http://localhost:5000/asr/api/v1.0/make_request'''
    print(cmd)
    op = run_command(cmd)    
    print(op)
    print("\n\n")

for v in x:
    p =str(np.random.randint(0,3))
    cmd = """/home/dalonlobo/workspace/ppevenv/bin/ppevenv/ds/bin/python /home/dalonlobo/deepspeech_models/asr/paddle_ds/cron_files/request_stt.py --conf_path /home/dalonlobo/deepspeech_models/asr/paddle_ds/cron_files/config.json --priority """+p+""" --storage_type blob --videoid """+v
    print(cmd)
    print()
    run_command(cmd)

# calculate wer
for v in x:
    p =str(np.random.randint(0,3))
    cmd = "/home/dalonlobo/workspace/ppevenv/bin/ppevenv/ds/bin/python compare_full_file_wers.py --ref ../paddle_ds/cron_files/tmp/41/"+v+"/"+v+".en.srt.ref.txt --hyp ../paddle_ds/cron_files/tmp/41/"+v+".en.srt.ref.txt"
    print(cmd)
    op = run_command(cmd)    
    print(op)
    print("\n\n")

# Value of the document
# {u'status': u'0', 
#u'_self': u'dbs/RsB7AA==/colls/RsB7AJLWwQE=/docs/RsB7AJLWwQEBAAAAAAAAAA==/',
# u'_ts': 1519123474,
# u'_rid': u'RsB7AJLWwQEBAAAAAAAAAA==',
# u'videoid': u'FmlPvVOR35k',
# u'_etag': u'"00009e01-0000-0000-0000-5a8bfc120000"',
# u'message': u'',
# u'_attachments': u'attachments/', 
# u'id': u'00df5b3d-8317-497e-87e0-4e0ab9fbd9d5'}
