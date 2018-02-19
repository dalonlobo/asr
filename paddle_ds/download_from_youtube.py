#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 11:13:22 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals
import os
import sys
import argparse
import logging

from custom_utils import run_command
from youtube_dl.utils import DownloadError

logger = logging.getLogger("__main__")

def download_video(destpath, videoid):
    """
    Download the video with youtube videoid
    """
    try:
        op_path = os.path.join(destpath, videoid)
        if not os.path.exists(op_path):
            os.makedirs(op_path)
        cmd = 'youtube-dl' + " -o '" + os.path.join(op_path, videoid) +\
                ".%(ext)s' -f mp4 --write-sub --sub-lang 'en' --convert-subs " + \
                "srt --write-auto-sub --write-info-json --prefer-ffmpeg " + \
                "https://www.youtube.com/watch?v=" + videoid
        logger.debug('Built cmd: ' + cmd)
        run_command(cmd)
        logger.info('Video {} downloaded successfully'.format(videoid))
    except DownloadError as e:
        logger.exception(e)
        logger.error("Could not download the following videos:")
        logger.error(videoid)
        sys.exit(-1)

if __name__ == "__main__":
    """
    This script will download the video in the given video id,
    :input:
        videoid : video id of youtube video
        dest_path : path where the video will be saved
    :run:
        python download_from_youtube.py --videoid FmlPvVOR35k --dest_path temp
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
        parser = argparse.ArgumentParser(description="Download video from youtube")
        parser.add_argument('--videoid', type=str,  
                            help='Youtube video Id')
        parser.add_argument('--dest_path', type=str,  
                        help='Path where video will be saved')
        args = parser.parse_args()    
        # Path to the destination folder, where videos will be saved 
        dest_path = os.path.abspath(args.dest_path)
        if not os.path.exists(dest_path):
            logger.info("Creating the directory: " + dest_path)
            os.makedirs(dest_path)
        download_video(dest_path, args.videoid)
        logger.info("Video {} downloaded successfully".format(args.videoid))
        print("Video downloaded successfully", file=sys.stderr)
        logger.info("############################################")
        logger.info(".....Exiting youtube downloader program.....")
        logger.info("#############################################")
        print(".....Exiting youtube downloader program.....", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        sys.exit(-1)
