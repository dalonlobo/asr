#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 11:04:13 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import os
import pandas as pd
import argparse
import sys
                            
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import split_on_silence

def split_on_silence_threshold(wav_file, dest_dir):
    """
    Splits the wav file in to chunks of wav files,
    based on the silence level
    Documentaion: http://pydub.com/
    Git: https://github.com/jiaaro/pydub/
    """
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
    chunks = split_on_silence(
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
    for index, chunk in enumerate(chunks):
        chunk_file_name = os.path.join(dest_dir, "sample_{}.wav".format(str(index).zfill(10)))
        print("Saving the file to " + chunk_file_name, file=sys.stderr)
        # You can export as mp3 etc, note that it has dependency on ffmpeg
        chunk.export(chunk_file_name, format="wav")

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
    parser = argparse.ArgumentParser(description="""
                                    Split the audio on silence""")
    parser.add_argument('--wav_file', '-w', type=str,  
                        help='Path to wave file')
    parser.add_argument('--dest_dir', '-d', type=str, default='tmp',  
                        help='Path to store the split segments')
#    args = parser.parse_args() # Uncomment this before running the file
    # Comment the following line before running the file
    args = parser.parse_args(["--wav_file", "/home/dalonlobo/deepspeech_models/asr/tmp_archive/verified_1_video/Videos/XtiYlNM9jRc/XtiYlNM9jRc.wav",\
                              "--dest_dir", "/home/dalonlobo/deepspeech_models/asr/cris_demo/split"])
    print("##########################", file=sys.stderr)
    print("....Starting program......", file=sys.stderr)
    print("##########################", file=sys.stderr)
    split_on_silence_threshold(args.wav_file, args.dest_dir)
    print("##########################", file=sys.stderr)
    print("....Program Completed.....", file=sys.stderr)
    print("##########################", file=sys.stderr)


