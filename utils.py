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

logger = logging.getLogger()
        
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
    # Remove the contents before :
    text = re.sub(r'.*:', '', text)
    # Remove contents inside the paranthesis
    text = re.sub(r"\([^)]*\)", '' , text)
    # Remove special characters
    text = re.sub('[^A-Za-z0-9\s\']+', ' ', text)
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
