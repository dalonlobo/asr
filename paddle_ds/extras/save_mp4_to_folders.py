#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 13:18:35 2018

@author: dalonlobo
"""

import glob
import os
import shutil

path = "/home/dalonlobo/paddle/DeepSpeech/OneDrive_1_08-02-2018/Skill2"

for file_name in glob.glob(path + os.path.sep + "*.mp4"):
    folder_name = os.path.basename(file_name).split(".")[0]
    print(folder_name)
    dest_folder = path + os.path.sep + folder_name
    os.mkdir(dest_folder)
    shutil.move(file_name, dest_folder + os.path.sep + os.path.basename(file_name))