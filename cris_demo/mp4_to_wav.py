#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 16:43:39 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging
import glob

from utils import convert_mp4_to_audio, run_command

logger = logging.getLogger("__main__")

def convert_video_to_audio(file_name):
    """Converts one srt to text file"""
    abs_path = os.path.dirname(file_name)
    op_name = os.path.basename(file_name) + ".wav"
    logger.info("Convertion started: " + file_name)
    cmd = convert_mp4_to_audio(file_name, os.path.join(abs_path,op_name))
    run_command(cmd)
    logger.info("Done converting: " + file_name)


if __name__ == "__main__":
    """
    This script will convert mp4 to wav files
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
                        help='Path to the folder mp4 files')
    # Remove the below line 
    args = parser.parse_args(["--srcpath", "Videos"])
    # Uncomment the below line
    # args = parser.parse_args()
    srcpath = os.path.abspath(args.srcpath)
    logger.debug("Reading the files: \n")
    for dirs in os.listdir(srcpath):
        vid_directory = os.path.join(srcpath, dirs)
        if not os.path.isdir(vid_directory):
            continue # If its not directory, just continue
        for file_name in glob.glob(vid_directory + os.path.sep + "*.mp4"):
            logger.info("Passing: " + file_name)
            convert_video_to_audio(file_name)
    logger.info("All mp4 converted")
    print("All mp4 converted", file=sys.stderr)
    logger.info("#########################")
    logger.info(".....Exiting program.....")
    logger.info("#########################")
    print(".....Exiting program.....", file=sys.stderr)
