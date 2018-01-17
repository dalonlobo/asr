#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 12:43:43 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging
import glob
import pandas as pd
import json
import requests
import traceback
import time

from utils import pre_process_srt
from requests.exceptions import ConnectionError

logger = logging.getLogger("__main__")  

def cris_stt(wav_folder, vid_directory):
    DELAY = 3 # Delay in seconds
    # Dataframe with all the transcripts
    transcripts = []
    for wav_file in glob.glob(wav_folder + os.path.sep + "*.wav"):
        try:
            DELAY = DELAY if DELAY <= 5 else 3
            logger.info("Uploading: " + wav_file)
            headers = {'Ocp-Apim-Subscription-Key': conf["Ocp-Apim-Subscription-Key"]}
            payload = open(wav_file, 'rb').read()
            print("Requesting", file=sys.stderr)
            r = requests.post(conf["url"], headers=headers, data=payload)
            transcripts.append((wav_file, wav_file.split("/")[-1], r.json()["DisplayText"]))
            logger.info("Transcription: " + str(transcripts[-1]))
            time.sleep(DELAY) # 1 second sleep to respect rate limit
        except ConnectionError as e:
            logger.exception(e)
            DELAY += 1
            time.sleep(5)
        except Exception as e:
            logger.error("Error:")
            logger.error(r.text)
            try:
                print(r.json(), file=sys.stderr)
                if r.json()["Message"].startswith("Too"):
                    time.sleep(5)
                    print("Trying again: " + wav_file, file=sys.stderr)
                    r = requests.post(conf["url"], headers=headers, data=payload)
                    transcripts.append((wav_file, wav_file.split("/")[-1], r.json()["DisplayText"]))
                    logger.info("Transcription: " + str(transcripts[-1]))
            except:
                pass
            traceback.print_exc()
            transcripts.append((wav_file, wav_file.split("/")[-1], ""))
            DELAY += 1
            time.sleep(5) # Give some time interval
        
    df = pd.DataFrame(data=transcripts, columns=["wav_path", "wav_name", "transcripts"])
    df.sort_values("wav_name", inplace=True)
    with open(os.path.join(vid_directory, 'cris_stt_df.xlsx'), 'w') as f:
        df.to_excel(f, index=False)
        
    with open(os.path.join(vid_directory, 'cris_hyp.txt'), 'w') as f:
        for trans in df["transcripts"]:
            f.write(pre_process_srt(trans) + " ")

if __name__ == "__main__":
    """
    Connect to cris endpoint
    Credentials are in json conf.json file 

    Ex: curl -X POST 
    "<url>" 
    -H "Transfer-Encoding: chunked" 
    -H "Ocp-Apim-Subscription-Key: <Subscription key>"
    -H "Content-type: audio/wav; codec=audio/pcm; samplerate=16000" 
    --data-binary @XtiYlNM9jRc_sample_0000000002.wav | jq   
    """
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
    parser.add_argument('--srcpath', type=str,  
                        help='Path to the folder wav files')
    # Remove the below line 
    args = parser.parse_args(["--srcpath", "Videos"])
    # Uncomment the below line
    # args = parser.parse_args()
    # Open the configuration file
    conf_path = "config.json"
    with open(conf_path, "r") as f:
        conf = json.load(f)
    srcpath = os.path.abspath(args.srcpath)
    logger.debug("Reading the files: \n")
    for dirs in os.listdir(srcpath):
        vid_directory = os.path.join(srcpath, dirs)
        split_directory = os.path.join(vid_directory, "custom_split")
        if not os.path.isdir(vid_directory):
            continue # If its not directory, just continue
        logger.info("Passing: " + split_directory)
        cris_stt(split_directory, vid_directory)
    logger.info("All wavs transcribed")
    print("All wav transcribed", file=sys.stderr)
    logger.info("#########################")
    logger.info(".....Exiting program.....")
    logger.info("#########################")
    print(".....Exiting program.....", file=sys.stderr)
