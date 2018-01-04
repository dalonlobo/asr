#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 15:06:43 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging

import pandas as pd

from timeit import default_timer as timer
from utils import run_command, convert_mp4_to_audio
from download_from_youtube import download_all_videos
from split_video_on_srt_time import split_video_on_srt_time
    
if __name__ == "__main__":
    """
    This script will download Sadguru videos, and preprocess them,
    3 folders will be created, train, dev and test, which will have the csv and 
    wav chunks
    """
    logs_path = os.path.basename(__file__) + ".logs"
    logging.basicConfig(filename=logs_path,
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    print("Logs are in ", os.path.abspath(logs_path), file=sys.stderr)
    print("Run the following command to view logs:", file=sys.stderr)
    print("tail -f {}".format(os.path.abspath(logs_path)), file=sys.stderr)
    try:
        logging.info("#########################")
        logging.info("....Starting program.....")
        logging.info("#########################")
        process_start_time = timer()
        parser = argparse.ArgumentParser(description="""
                                         This script will import sadguru videos and preprocess them, 
                                         so that you can train deepspeech model""")
        parser.add_argument('--vidlist', type=str,  
                            help='Path to the excel file containing list of videos to download')
        parser.add_argument('--destpath', type=str,  
                            help='Path to store the video files')
        parser.add_argument('--checkpoint_dir', type=str,  
                            help='Path to checkpoint direcotry')
        args = parser.parse_args(["--vidlist", "SADHGuru Channel Videos.xlsx",
                                  "--checkpoint_dir", "tmp/checkpoint",
                                  "--destpath", "tmp"])
        # Path to the checkpoint directory
        checkpoint_dir = args.checkpoint_dir
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        checkpoint_dir = os.path.abspath(checkpoint_dir)
        # Path to the destination folder, where videos will be saved 
        destpath = os.path.abspath(args.destpath)
        # path to excel  file containing the list of videos to download
        vidlist = os.path.abspath(args.vidlist)   
        # Videos will be stored here
        videospath = os.path.join(os.path.abspath(args.destpath), "Videos")
        # Create the destination folder if it does not exist
        if not os.path.exists(videospath):
            logging.info("Creating the directory: " + videospath)
            os.makedirs(videospath)
        else:
            print("Videos directory already exists", file=sys.stderr)
            try:
               input = raw_input # Py 2 and 3 compatibility
            except NameError:
               pass
            user_input = input("Do you want to continue? y or n\n")
            if user_input != "y":
                sys.exit(0)
                
        # Read the videos list from excel file
        # Columns are VideoID,	Link, 	Transcribed
        df_to_download = pd.read_excel(vidlist)    
        # Retain only the videos which have transcription
        df_to_download = df_to_download[df_to_download.Transcribed == 1]
        logging.debug("List of videos that will be downloaded: ")
        logging.debug(df_to_download.Link)
        logging.info("Saving the videos to: " + videospath)
        # Download all the videos in the list to the destination folder
        flag = download_all_videos(videospath, df_to_download)
        if not flag:
            logging.error("Download the videos again, something went wrong!")
            print("Download the videos again, something went wrong!", file=sys.stderr)
            sys.exit(-1)
        # Splitting the videos 
        for dirs in os.listdir(videospath):
            directory = os.path.join(videospath, dirs)
            logging.info("Splitting the video in following directory:")
            logging.info(directory)
            split_video_on_srt_time(videospath, checkpoint_dir, directory, dirs)
        print("All the videos are converted to audio and split successfully", file=sys.stderr)
        logging.info('Entire program ran in {} minutes'.format((timer() - process_start_time) / 60))
    except SystemExit as e:
        print("System exit command issued with code: " + str(e), file=sys.stderr)
        logging.error("System exit command issued with code: " + str(e))
    finally:
        logging.info("#########################")
        logging.info(".....Exiting program.....")
        logging.info("#########################")
        print("#### Exiting Program ####", file=sys.stderr)
    
    
    
    
    
    
    
    
    
    
