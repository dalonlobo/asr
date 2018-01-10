#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:10:12 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import logging
import subprocess
import re
import numpy as np
import pandas as pd
import pysrt
import zipfile

from distutils.dir_util import copy_tree

logger = logging.getLogger("__main__")
        
def convert_mp4_to_audio(fpath_in, fpath_out):
    """Convert to wav format with 1 channel and 16Khz freq"""
    cmd = "ffmpeg -i '" + fpath_in + "' -ar 16000 -ac 1 '" + fpath_out + "'"
    logger.debug("Command: " + cmd)
    return cmd

def run_command(command):
    logger.debug("Executing: " + command)
    p = subprocess.Popen(command, bufsize=2048, shell=True, 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         close_fds=(sys.platform != 'win32'))
    output = p.communicate()
    logger.debug("Execution completed: " + command[:30] + "...")
    return output

def convert_to_ms(st):
    """Converts the subtitle time to millisecond"""
    return (st.hours * 60 * 60 * 1000) + (st.minutes * 60 * 1000) +\
                  (st.seconds * 1000) + (st.milliseconds)
                  
def pre_process_srt(text):
    # Replace the unicodes 
    text = text.replace(u"\u2018", "'").replace(u"\u2019", "'")
    # Remove the contents before :
    text = re.sub(r'.*:', '', text)
    # Remove contents inside the paranthesis
    text = re.sub(r"\([^)]*\)", '' , text)
    # Remove special characters and digits
    text = re.sub('[^A-Za-z\s\']+', ' ', text)
    # Remove newline characters
    text = re.sub(r'\n', ' ', text)
    return text.lower().strip()

def train_validate_test_split(df, train_percent=.6, validate_percent=.2, seed=None):
    np.random.seed(seed)
    perm = np.random.permutation(df.index)
    m = len(df)
    train_end = int(train_percent * m)
    validate_end = int(validate_percent * m) + train_end
    train = df.iloc[perm[:train_end]]
    validate = df.iloc[perm[train_end:validate_end]]
    test = df.iloc[perm[validate_end:]]
    return train, validate, test

def clean_srt_min_duration(srt_file, DURATION=1000):
    """
    This will merge the subtitles which are less than DURATION,
    DURATION should be in milliseconds
    """
    subs = pysrt.open(srt_file)
    indexes_to_delete = []
    for index, sub in enumerate(subs[:-1]):
        duration = sub.duration
        # convert duration to seconds
        if duration.seconds * 1000 + duration.milliseconds < DURATION:
            logger.debug("Duration is less than 1s: "+ str(duration.seconds * 1000 + duration.milliseconds))
            # Check the next sub duration and append it to that
            # If the next duration is greater than 5s, don't do anything
            next_duration = subs[index + 1].duration
            if next_duration.seconds * 1000 + next_duration.milliseconds >= 5000:
                continue
            sub.text += " " + subs[index + 1].text
            sub.end = subs[index + 1].end # extend this subtitle
            indexes_to_delete.append(index + 1)
    logger.debug("Indexes to delete: ")
    logger.debug(indexes_to_delete)
    subs = [sub for index, sub in enumerate(subs) if index not in  indexes_to_delete]
    subs = pysrt.srtfile.SubRipFile(subs) # Convert the list to srt
    subs.clean_indexes() # cleanup the indexes
    subs.save(srt_file) # Save to same srt file
            
def copy_contents(source, destination):
    "Copy the contents of source to destination"
    copy_tree(source, destination)
    return True
    
def zipdir(path, ziph):
    " ziph is zipfile handle "
    for files in os.listdir(path):
        ziph.write(os.path.join(path, files))
    
    
    
    