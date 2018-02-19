#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 15:06:25 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging
import pysrt
import glob

from custom_utils import pre_process_srt

logger = logging.getLogger("__main__")

def convert_srt(file_name):
    """Converts one srt to text file"""
    abs_path = os.path.dirname(file_name)
    op_name = os.path.basename(file_name) + ".ref.txt"
    # Read the srt file
    subtitles = pysrt.open(file_name)
    logger.info("Read the srt file " + file_name)
    with open(os.path.join(abs_path,op_name), "w") as f:
        for index, subtitle in enumerate(subtitles):
            sub = pre_process_srt(subtitle.text)
            f.write(sub + " " if sub else "")
    logger.info("Done writing to text: " + file_name)
    

if __name__ == "__main__":
    """
    This script will convert all srt files in all subfolders to text files
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
    parser = argparse.ArgumentParser(description="Download videos from youtube")
    parser.add_argument('--srcpath', type=str,  
                        help='Path to the folder containing srt files')
    # Remove the below line 
    args = parser.parse_args(["--srcpath", "Videos"])
    # Uncomment the below line
    # args = parser.parse_args()
    # Path to the source folder, where srt will be saved 
    srcpath = os.path.abspath(args.srcpath)
    logger.debug("Reading the files: \n")
    for dirs in os.listdir(srcpath):
        vid_directory = os.path.join(srcpath, dirs)
        if not os.path.isdir(vid_directory):
            continue # If its not directory, just continue
        for file_name in glob.glob(vid_directory + os.path.sep + "*.srt"):
            logger.info("Passing: " + file_name)
            convert_srt(file_name)
    logger.info("All srt files converted")
    print("All srt files converted", file=sys.stderr)
    logger.info("#########################")
    logger.info(".....Exiting program.....")
    logger.info("#########################")
    print(".....Exiting program.....", file=sys.stderr)
