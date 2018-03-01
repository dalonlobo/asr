#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 1 11:13:22 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import json
import argparse
import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors

from logging.config import dictConfig
from datetime import datetime
from flask import Flask, jsonify, request, abort, make_response

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

class IDisposable:
    """
    A context manager to automatically close an object with a close method
    in a with statement. 
    """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None

@app.route('/')
def index():
    return "To make request use: /asr/api/v1.0/make_request"

# Insert into the cosmos db
def createUpdateDocument(videoid, videourl, priority):
    # Write into the db
    with IDisposable(document_client.DocumentClient(HOST, \
                                                    {'masterKey': MASTER_KEY})) as client:
        videoJSON = {"videoid": videoid,
                     "videourl": videourl,
                     "status": "0",
                     "priority": priority,
                     "timestamp": str(datetime.utcnow().isoformat()[:-3]),
                     "message": ""}
        query = "SELECT * FROM "+DS_JOB_COLLECTION_ID+" t  "+\
                "WHERE t.videoid = '"+videoid+"'"
        documentlist = list(client.QueryDocuments(job_collection_link, query))
        if len(documentlist):
            videoJSON["id"] = documentlist[0]["id"]
            return client.UpsertDocument(job_collection_link, videoJSON)
        else:
            return client.CreateDocument(job_collection_link, videoJSON) 

# Read from the cosmos db
def getDocument(document_id):
    # Write into the db
    with IDisposable(document_client.DocumentClient(HOST, \
                                                    {'masterKey': MASTER_KEY})) as client:
        options = {} 
        query = "SELECT * FROM "+DS_JOB_COLLECTION_ID+" t WHERE t.id='"+str(document_id)+"'"
        documentlist = list(client.QueryDocuments(job_collection_link, query, options))
        return documentlist
    

@app.route('/asr/api/v1.0/make_request', methods=['POST'])
def make_asr_request():
    app.logger.debug("Received a make_request with json:")
    app.logger.debug(request.json)
    if not request.json or not 'video_id' in request.json:
        app.logger.error("No json or video_id is not passed")
        abort(400)
    app.logger.debug(request.json.get("video_id"))
    video_id = request.json.get("video_id")
    video_url = request.json.get("url", "")
    priority = request.json.get("url", "0") # Default priority is Low i.e. 0
    resDict = createUpdateDocument(video_id, video_url, priority)
    app.logger.debug(resDict)
    response = {
        "id": resDict.get("id")
    }
    return jsonify(response), 201


@app.route('/asr/api/v1.0/get_status', methods=['GET'])
def get_status():
    document_id = request.args.get('document_id', default = '', type = str)
    app.logger.debug("Received get_status request for:")
    app.logger.debug(document_id)
    if not len(document_id):
        app.logger.error("Document id is not passed")
        abort(400)
    documentlist = getDocument(document_id)
    app.logger.debug(documentlist)
    if len(documentlist) == 0:
        abort(404)
    return jsonify(documentlist)

@app.errorhandler(400)
def error_400(error):
    return make_response(jsonify({'error': 'Check the request you made'}), 400)

if __name__ == '__main__':
    """
    This REST server will make a request to ASR engine.
    :APIs available:
    1
    :URL: /asr/api/v1.0/make_request
    :Type: POST
    :Body: JSON object
        :JSON:
            {
                "video_id": "###ABC",
                "url": "url to download the video", # Could be blob|youtube
                "priority": "0|1|2, 2-Highest, 1-Medium, 0-Low"
            }
    :Response:
        :JSON:
            {
                "id": "Cosmos db document id"
            }
    :Testing using curl:
        curl -i -H "Content-Type: application/json" -X POST -d '{"video_id":"###"}' http://localhost:5000/asr/api/v1.0/make_request
    
    2
    :URL: /asr/api/v1.0/get_status/<int:document_id>
    :Type: GET
    :Body: None
    :Response:
        :JSON with document details:
    :Testing using curl:
        curl -i http://localhost:5000/asr/api/v1.0/get_status?document_id=#####
    """
    parser = argparse.ArgumentParser(description="Flask server")
    parser.add_argument('--conf_path', type=str,  
                        help='path to configuration file')
    args = parser.parse_args()
    # Path to the configuration file
    conf_path = args.conf_path
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "flask_server.logs"),
            'maxBytes': 10 * 1000000,
            'backupCount': 5,
            'formatter': 'default'
        }},
        'root': {
            'level': 'DEBUG',
            'handlers': ['wsgi']
        }
    })

    # Read the configuration file
    with open(conf_path, "r") as f:
        conf = json.load(f)
        HOST = conf["HOST"]
        MASTER_KEY = conf["MASTER_KEY"]
        DATABASE_ID = conf["DATABASE_ID"]
        DS_JOB_COLLECTION_ID = conf["DS_JOB_COLLECTION_ID"]
        database_link = 'dbs/' + DATABASE_ID
        job_collection_link = database_link + '/colls/' + DS_JOB_COLLECTION_ID

    app.run(debug=True)
