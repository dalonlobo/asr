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
import sys
import os
import pickle

from datetime import datetime, timedelta

def print_time(secs):
    sec = timedelta(seconds=secs)
    d = datetime(1,1,1) + sec
    print("DAYS:HOURS:MIN:SEC")
    print("%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second))

def duration(fpath, above_5s):
    print("Calculating duration: ", fpath)
    total_duration = 0
    print("Total files: ", len(glob.glob(fpath + '/*.wav')))
    try:
        for files in glob.glob(fpath + '/*.wav'):
            with contextlib.closing(wave.open(files,'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                file_duration = frames / float(rate)
                above_5s.append(file_duration)
                total_duration += file_duration
    except:
        pass
    return (total_duration, above_5s)

if __name__ == "__main__":    
    fpath = sys.argv[1]
    print(fpath)
    duration_s = 0
    above_5s = []
    for dirs in os.listdir(fpath):
        directory = os.path.join(fpath, dirs)
        if not os.path.isdir(directory):
            continue # If its not directory, just continue
        dur, above_5s = duration(os.path.join(directory,"samples"), above_5s)
        duration_s += dur
    print()
    print("Max duration of files: ",max(above_5s))
    print("Number of files above 5s: ",len(above_5s))
    print()
    with open("wav_greater_than_5_"+datetime.now().strftime('%Y-%m-%d-%H-%M')+".b",'wb') as f:
        pickle.dump(above_5s, f)   
        print("Above 5s list is pickled")
    print("Total duration in hours {}hrs".format((duration_s/60)/60))
    print_time(int(duration_s))

