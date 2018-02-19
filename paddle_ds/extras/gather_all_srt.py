#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 15:32:37 2018

@author: dalonlobo
"""

import glob
import os
import shutil
import argparse

parser = argparse.ArgumentParser(description="gather srt")
parser.add_argument('--srcpath', type=str,  
                    help='Path to the folder')
parser.add_argument('--dest_path', type=str,  
                    help='Path to the dest folder')
args = parser.parse_args()

path = args.srcpath
dest_directory = args.dest_path

if not os.path.exists(dest_directory):
    os.mkdir(dest_directory)

for dirs in os.listdir(path):
    vid_directory = os.path.join(path, dirs)
    if not os.path.isdir(vid_directory):
        continue # If its not directory, just continue
    for file_name in glob.glob(vid_directory + os.path.sep + "*.srt"):
        shutil.copy(file_name, dest_directory)