#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 10:10:22 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals
import os
import sys
import argparse
import logging

from custom_utils import run_command

logger = logging.getLogger("__main__")

def download_video(videoid, dest_path):
    """
    Download the video
    """
    cmd = 'python download_from_youtube.py --videoid '+videoid\
            +' --dest_path ' + dest_path
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

def mp4_to_flac(srcpath):
    """
    Convert mp4 files to flac
    """
    cmd = 'python mp4_to_flac.py --srcpath '+srcpath
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

def split_on_silence(srcpath):
    """
    Split on silence
    """
    cmd = 'python split_on_silence.py --srcpath '+srcpath
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

def stt(srcpath):
    """
    Deep Speech
    """
    cmd = "CUDA_VISIBLE_DEVICES=0 python ds2_stt.py --trainer_count 1 "+\
    "--num_conv_layers=2 --num_rnn_layers=3 --rnn_layer_size=1024 "+\
    "--use_gru=True --share_rnn_weights=False --specgram_type='linear' "+\
    "--mean_std_path=/Deepspeech/baidu_en8k_model/mean_std.npz "+\
    "--vocab_path=/Deepspeech/baidu_en8k_model/vocab.txt "+\
    "--lang_model_path=/DeepSpeech/common_crawl_00.prune01111.trie.klm "+\
    "--model_path=/DeepSpeech/baidu_en8k_model/params.tar.gz "+\
    "--src_path=" + srcpath
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

def create_srt(srcpath):
    """
    Create srt
    """
    cmd = 'python create_srt.py --srcpath '+srcpath
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

if __name__ == "__main__":
    """
    This script will run the entire pipeline of speech to text
    :input:
        videoid : video id of youtube video
    :run:
        python stt_pipeline.py --videoid FmlPvVOR35k
    """
    try:
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
        parser = argparse.ArgumentParser(description="Speech to text")
        parser.add_argument('--videoid', type=str,  
                            help='Youtube video Id')
        args = parser.parse_args()    
        # Path to the destination folder, where videos will be saved 
        dest_path = os.path.abspath("tmp")
        if not os.path.exists(dest_path):
            logger.info("Creating the directory: " + dest_path)
            os.makedirs(dest_path)
        video_path = os.path.join(dest_path, args.videoid)
        exit_code, output = download_video(args.videoid, dest_path)
        logger.info("Video downloaded with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in video downloading")
            
        # Convert mp4 to flac
        exit_code, output = mp4_to_flac(video_path)
        logger.info("Mp4 to flac exited with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in converting mp4 to flac")
            
        # split on silence
        exit_code, output = split_on_silence(video_path)
        logger.info("split on silence exited with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in spliting on silence")
            
        # Use deepspeech 2
        exit_code, output = stt(video_path)
        logger.info("ds2_stt.py exited with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in deepspeech")        

        # create srt
        exit_code, output = create_srt(video_path)
        logger.info("create_srt.py exited with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in srt creation")  
        
        logger.info("Stt successful".format(args.videoid))
        print("Stt successful", file=sys.stderr)
        logger.info("############################################")
        logger.info(".....Exiting stt pipeline program.....")
        logger.info("#############################################")
        print(".....Exiting stt pipeline program.....", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)

