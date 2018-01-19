#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 11:04:13 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging
import glob
import pickle
import pandas as pd

from utils import convert_mp4_to_audio, run_command
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import detect_nonsilent

logger = logging.getLogger("__main__")     

def split_on_silence_custom(audio_segment, min_silence_len=1000, silence_thresh=-16, keep_silence=100,
                     seek_step=1):
    """
    audio_segment - original pydub.AudioSegment() object
    min_silence_len - (in ms) minimum length of a silence to be used for
        a split. default: 1000ms
    silence_thresh - (in dBFS) anything quieter than this will be
        considered silence. default: -16dBFS
    keep_silence - (in ms) amount of silence to leave at the beginning
        and end of the chunks. Keeps the sound from sounding like it is
        abruptly cut off. (default: 100ms)
    return chunk=((chunk, start, end))
    """

    not_silence_ranges = detect_nonsilent(audio_segment, min_silence_len, silence_thresh)

    chunks = []
    for start_i, end_i in not_silence_ranges:
        start_i = max(0, start_i - keep_silence)
        end_i += keep_silence
        chunks.append((audio_segment[start_i:end_i], start_i, end_i))

    return chunks

def split_on_silence_threshold(wav_file):
    """
    Splits the wav file in to chunks of wav files,
    based on the silence level
    Documentaion: http://pydub.com/
    Git: https://github.com/jiaaro/pydub/
    """
    abs_path = os.path.dirname(wav_file)
    dest_dir = os.path.join(abs_path, "custom_split")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    logger.info("Splitting started: " + wav_file)    
    # Read the file
    audioSegment = AudioSegment.from_wav(wav_file)
    # Calculating the silence threshold
    # Normalizing the audio file belfore finding the threshold
    full_audio_wav = normalize(audioSegment)
    loudness_ms_list = [] # Save the audio levels of all the chunks
    for ms_chunk in full_audio_wav:
        loudness_ms_list.append(round(ms_chunk.dBFS))
    print("Audio levels are recorded", file=sys.stderr)
    # Using pandas df for easier manipulation
    df = pd.DataFrame(loudness_ms_list)
    df[0] = df[df[0] != float("-inf")] # Remove the very low levels
    st = df[0].mean()
    st = st if st < -16 else -16 # Because -16db is default
    # Splits the audio if silence duration is MSL long
    MSL = 500 # minimum silence length in ms
    print("Splitting into silence chunks", file=sys.stderr)
    chunks = split_on_silence_custom(
        full_audio_wav,    
        # split on silences longer than 500ms (500ms)
        min_silence_len=MSL,    
        # anything under -16 dBFS is considered silence
        silence_thresh=st,      
        # keep 200 ms of leading/trailing silence
        keep_silence=200,       
        )
    # Saving all the chunks
    print("Writing all the files, this may take some time!", file=sys.stderr)
    # save start and end time aswell
    split_durations = []
    for index, chunk in enumerate(chunks):
        chunk_file_name = os.path.join(dest_dir, "sample_{}.wav".format(str(index).zfill(10)))
        print("Saving the file to " + chunk_file_name, file=sys.stderr)
        # You can export as mp3 etc, note that it has dependency on ffmpeg
        chunk[0].export(chunk_file_name, format="wav")
        split_durations.append((chunk_file_name, chunk_file_name.split("/")[-1],\
                                chunk[1], chunk[2]))
    try:
        with open(os.path.join(abs_path, "split_durations.b"), "wb") as f:
            pickle.dump(split_durations, f)
    except:
        pass    
    try:
        with open(os.path.join(abs_path, "split_df.csv"), "wb") as f:
            df = pd.DataFrame(split_durations, columns=["wav_filepath", "wav_filename",\
                                                        "start", "end"])
            df.to_csv(f, index=False)
            print("Split df saved to: ", os.path.join(abs_path, "split_df.csv"),\
                  file=sys.stderr)
    except:
        pass
    
def _future_work_():
    """
    -> You can use detect_nonsilent or detect_nonsilent from silence module
    for still custom splits.
    Git: https://github.com/jiaaro/pydub/blob/master/pydub/silence.py
    -> You can apply first order low_pass_filter, high_pass_filter for noise reduction
    from effects module. Many other functions like speedup, invert_phase etc are also
    available in that module.
    -> For higher order low_pass_filter and high_pass_filter please use it from
    scipy_effects module. 
    Git: https://github.com/jiaaro/pydub/blob/master/pydub/scipy_effects.py
    """
    pass

if __name__ == "__main__":
    """
    Split wavs on silence
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
    args = parser.parse_args(["--srcpath", "Videos"])
    # Uncomment the below line
    # args = parser.parse_args()
    srcpath = os.path.abspath(args.srcpath)
    logger.debug("Reading the files: \n")
    for dirs in os.listdir(srcpath):
        vid_directory = os.path.join(srcpath, dirs)
        if not os.path.isdir(vid_directory):
            continue # If its not directory, just continue
        for file_name in glob.glob(vid_directory + os.path.sep + "*.wav"):
            logger.info("Passing: " + file_name)
            split_on_silence_threshold(file_name)
    logger.info("All mp4 converted")
    print("All mp4 converted", file=sys.stderr)
    logger.info("#########################")
    logger.info(".....Exiting program.....")
    logger.info("#########################")
    print(".....Exiting program.....", file=sys.stderr)


