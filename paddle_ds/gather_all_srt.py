#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 15:32:37 2018

@author: dalonlobo
"""

import glob
import os
import shutil

path = "/home/dalonlobo/paddle/DeepSpeech/OneDrive_1_08-02-2018/Skill2"

dest_directory = "Skill2_srts"

if not os.path.exists(dest_directory):
    os.mkdir(dest_directory)

for dirs in os.listdir(path):
    vid_directory = os.path.join(path, dirs)
    if not os.path.isdir(vid_directory):
        continue # If its not directory, just continue
    for file_name in glob.glob(vid_directory + os.path.sep + "*.srt"):
        shutil.copy(file_name, dest_directory)