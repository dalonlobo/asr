#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 12:45:49 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging
import glob
import pysrt
import pandas as pd
import pickle

from utils import run_command, convert_mp4_to_audio, convert_to_ms, \
                    pre_process_srt
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import split_on_silence

logger = logging.getLogger("__main__")

def split_video_on_srt_time(basedirectory, checkpoint_dir, directory, videoid):
    try:
        # Path to the mp4 file
        mp4_fpath = glob.glob(directory + "/*.mp4")[0]
        # Path to the srt file
        srt_fpath = glob.glob(directory + "/*.srt")[0]
    except IndexError as e:
        logger.exception(e)
        logger.error("Either mp4 or srt file is missing for " + videoid)
        return
    # Path to wav file
    output_wav_path = os.path.join(directory, videoid + ".wav")
    logger.debug("Different paths are:")
    logger.debug("mp4_fpath: " + mp4_fpath)
    logger.debug("srt_fpath: " + srt_fpath)
    logger.debug("output_wav_path: " + output_wav_path)
    logger.info("Converting {} to {}".format(mp4_fpath, output_wav_path))
    # Converting mp4 to wav
    run_command(\
                convert_mp4_to_audio(mp4_fpath, output_wav_path))
    # Audio segments
    audio_segments = AudioSegment.from_wav(output_wav_path)
    # Save the audio segments here
    samples_path = os.path.join(directory, "samples")
    logger.debug("Directory for audio segments: " + samples_path)
    if not os.path.exists(samples_path):
        os.makedirs(samples_path)
    # Read the srt file
    subtitles = pysrt.open(srt_fpath)
    # Buffer in milliseconds to append to start and end of each segment
    BUFFER_IN_MS = 250
    # Entire list of tuple Path_to_wav,size,transcript
    data_to_df = []
    for index, subtitle in enumerate(subtitles):
        logger.debug("Processing subtitle number: {}".format(index + 1))
        # Convert to milliseconds
        start_in_ms = convert_to_ms(subtitle.start) + BUFFER_IN_MS                          
        end_in_ms = convert_to_ms(subtitle.end) + BUFFER_IN_MS
        logger.debug("This audio segment is from {}ms to {}ms".format(start_in_ms, end_in_ms))
        # pydub segments are in milliseconds
        segment = audio_segments[start_in_ms:end_in_ms]
        # Path to the audio segment
        segment_path = os.path.join(samples_path, "sample_{}.wav".format(str(index).zfill(10)))
        # check if the segment is greater than 5s
        duration = end_in_ms - start_in_ms
        if duration > 5000:
            logger.info("Segment {} is greater than 5s, its {}ms long".format(segment_path, duration))
        # Export as wav
        segment.export(segment_path, format="wav") 
        # Format to save to csv
        # Path_to_wav,size,transcript
        temp_tuple = (segment_path,os.path.getsize(segment_path),pre_process_srt(subtitle.text))
        logger.info("Data:")
        logger.info(temp_tuple)
        data_to_df.append(temp_tuple)
    # Save the list 
    with open(os.path.join(checkpoint_dir, videoid + "_data.b"), "wb") as f:
        pickle.dump(data_to_df, f)
    # Convert the list to pandas dataframe
    df = pd.DataFrame(data=data_to_df, columns=["wav_filename", "wav_filesize", "transcript"])
    # Save dataframe as csv
    logger.info("Saving the data to: "+os.path.join(basedirectory, videoid + "_data.csv"))
    df.to_csv(os.path.join(basedirectory, videoid + "_data.csv"), index=False)
    logger.info("Processing of video {} done".format(videoid))
    return True
    
    
        
        
        
        
        
        
        
        
        
