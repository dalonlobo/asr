#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 15:52:33 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging
import pandas as pd
from pysrt.srtfile import SubRipFile
from pysrt.srtitem import SubRipItem
from pysrt.srtitem import SubRipTime

logger = logging.getLogger("__main__")    

def create_srt(split_df, cris_stt_df):
    abs_path = os.path.dirname(split_df)
    df1 = pd.read_csv(split_df)
    df2 = pd.read_excel(cris_stt_df)
    df1.rename(columns={'wav_filename': 'wav_name'}, inplace=True)
    # This df3 contains all the info for srt creation
    df3 = pd.merge(df1, df2,  how='inner', on='wav_name')
    print("Creating the srt:")
    new_srt = SubRipFile()
    for index, row in df3.iterrows():
        text = str(row['transcripts'] if \
                    type(row['transcripts']) != float \
                        else "")
        new_srt.append(SubRipItem(index=index+1,
                              start=SubRipTime(milliseconds=row['start']),
                              end=SubRipTime(milliseconds=row['end']),
                              text=text[:-1] if text.endswith(".") else text
                                ))
    new_srt.save(os.path.join(abs_path, "stt_converted.srt"))
    print("successfully written")

if __name__ == "__main__":
    """
    Create srt files
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
    # args = parser.parse_args(["--srcpath", "Videos"])
    # Uncomment the below line
    args = parser.parse_args()
    srcpath = os.path.abspath(args.srcpath)
    logger.debug("Reading the files: \n")
    for dirs in os.listdir(srcpath):
        vid_directory = os.path.join(srcpath, dirs)
        if not os.path.isdir(vid_directory):
            continue # If its not directory, just continue
        split_df = os.path.join(vid_directory, "split_df.csv")
        cris_stt_df = os.path.join(vid_directory, "cris_stt_df.xlsx")
        print("Reading files:")
        print(split_df, cris_stt_df, sep="\n")
        create_srt(split_df, cris_stt_df)
    logger.info("All srt converted")
    print("All srt converted", file=sys.stderr)
    logger.info("#########################")
    logger.info(".....Exiting program.....")
    logger.info("#########################")
    print(".....Exiting program.....", file=sys.stderr)
