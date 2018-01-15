#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 12:57:47 2018

@author: dalonlobo
"""
from __future__ import print_function, division
import wave
import contextlib
import glob
from datetime import datetime, timedelta

def print_time(secs):
    sec = timedelta(seconds=secs)
    d = datetime(1,1,1) + sec
    print("DAYS:HOURS:MIN:SEC")
    print("%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second))

total_duration = 0
for files in glob.glob('/home/dalonlobo/deepspeech_models/asr/tmp_archive/175_samples/*.wav'):
    with contextlib.closing(wave.open(files,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        total_duration += duration
        
print("Total duration in hours {}hrs".format((total_duration/60)/60))
print_time(int(total_duration))

