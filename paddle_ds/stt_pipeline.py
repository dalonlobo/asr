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
import shutil
import json

from azure.storage.blob import BlockBlobService
from datetime import datetime
from custom_utils import run_command

logger = logging.getLogger("__main__")


class AzureStorageInterface:


    def __init__(self, AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY,\
                 AZURE_DIRECTORY_NAME, AZURE_CONTAINER_NAME):
        self.AZURE_ACCOUNT_KEY = AZURE_ACCOUNT_KEY
        self.AZURE_ACCOUNT_NAME = AZURE_ACCOUNT_NAME
        self.AZURE_DIRECTORY_NAME = AZURE_DIRECTORY_NAME
        self.AZURE_CONTAINER_NAME = AZURE_CONTAINER_NAME        
        self.block_blob_service = BlockBlobService(AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY)


    def updateSRTFiles (self, videoid, srtFilePath):
        #.2017-05-22T15:18:29.573
        self.createBlob(videoid, srtFilePath)
        print("Updated SRT file for videoid ", videoid, srtFilePath)
        timedSRTFILEPATH = srtFilePath + '.' + str(datetime.utcnow().isoformat()[:-3])
        shutil.copy(srtFilePath, timedSRTFILEPATH)
        self.createBlob(videoid, timedSRTFILEPATH)
        print("Updated SRT file for videoid ", videoid, timedSRTFILEPATH)        


    def getVideoFilesFromAzureStorage(self, videoid, videodirpath):
        videoblobname = self.AZURE_DIRECTORY_NAME + videoid + '/' + videoid + '.mp4'
        if not os.path.exists(videodirpath):
            os.makedirs(videodirpath)
        videopath =  videodirpath + "/"+ videoid + '.mp4'
        if self.block_blob_service.exists(self.AZURE_CONTAINER_NAME, videoblobname):
            self.getBlob(videoblobname, videopath)
        if os.path.exists (videopath):
            return True, videopath
        else:
            return False, ''


    def isSRTExist(self, videoid):
        srtblobname =  self.AZURE_DIRECTORY_NAME + videoid + '/' + videoid + '.en.srt'
        issrtexist = self.block_blob_service.exists(self.AZURE_CONTAINER_NAME, srtblobname)
        return issrtexist
    

    def isVideoExist(self, videoid):
        videoblobname =  self.AZURE_DIRECTORY_NAME + videoid + '/' + videoid + ".mp4"
        isvideoexist = self.block_blob_service.exists(self.AZURE_CONTAINER_NAME, videoblobname)
        return isvideoexist


    def deleteBlob(self, blobname):
        self.block_blob_service.delete_blob(self.AZURE_CONTAINER_NAME, blobname)


    def getBlob(self, blobname, filepath):
        self.block_blob_service.get_blob_to_path(self.AZURE_CONTAINER_NAME, blobname,filepath)
        

    def createBlob(self, videoid, filepath):
        path, filename = os.path.split(filepath)
        blobname = self.AZURE_DIRECTORY_NAME + videoid + '/' + filename 
        self.block_blob_service.create_blob_from_path(self.AZURE_CONTAINER_NAME, blobname, filepath)


def download_youtube_video(videoid, dest_path):
    """
    Download the video
    """
    cmd = 'python /Deepspeech/download_from_youtube.py --videoid '+videoid\
            +' --dest_path ' + dest_path
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

def mp4_to_flac(srcpath):
    """
    Convert mp4 files to flac
    """
    cmd = 'python /Deepspeech/mp4_to_flac.py --srcpath '+srcpath
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

def split_on_silence(srcpath):
    """
    Split on silence
    """
    cmd = 'python /Deepspeech/split_on_silence.py --srcpath '+srcpath
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

def stt(srcpath):
    """
    Deep Speech
    """
    cmd = "CUDA_VISIBLE_DEVICES=0 python /Deepspeech/ds2_stt.py --trainer_count 1 "+\
    "--num_conv_layers=2 --num_rnn_layers=3 --rnn_layer_size=1024 "+\
    "--use_gru=True --share_rnn_weights=False --specgram_type='linear' "+\
    "--mean_std_path=/Deepspeech/mean_std.npz "+\
    "--vocab_path=/Deepspeech/vocab.txt "+\
    "--lang_model_path=/Deepspeech/common_crawl_00.prune01111.trie.klm "+\
    "--model_path=/Deepspeech/params.tar.gz "+\
    "--manifest_path="+srcpath+"/manifest.txt "+\
    "--src_path=" + srcpath
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

def create_srt(srcpath):
    """
    Create srt
    """
    cmd = 'python /Deepspeech/create_srt.py --srcpath '+srcpath
    logger.debug('Built cmd: ' + cmd)
    return run_command(cmd)

if __name__ == "__main__":
    """
    This script will run the entire pipeline of speech to text
    :Steps in the Pipeline:
        1. Download video from given id
        2. Convert the mp4 to flac
        3. Split the flac on the silence
        4. Run deepspeech 2 model on the split files
        5. Create the srt file
    :input:
        videoid : video id of youtube video
        storage_type: youtube or blob
        conf_path: path to the configuration file
    :run:
        python stt_pipeline.py --videoid FmlPvVOR35k --storage_type youtube --conf_path conf.json
    """
    try:
        logs_path = "/Deepspeech/"+os.path.basename(__file__) + ".logs"
        logging.basicConfig(filename=logs_path,
            filemode='a',
            format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        print("Logs are in ", os.path.abspath(logs_path), file=sys.stderr)
        print("Run the following command to view logs:\n", file=sys.stderr)
        print("tail -f {}".format(os.path.abspath(logs_path)), file=sys.stderr)
        parser = argparse.ArgumentParser(description="Speech to text")
        parser.add_argument('--videoid', type=str,  
                            help='Youtube video Id')
        parser.add_argument('--storage_type', type=str,  
                            help='Youtube video Id')
        parser.add_argument('--conf_path', type=str,  
                            help='Path to configuration file')
        args = parser.parse_args()    
        logger.info("Starting the program")
        # Path to the destination folder, where videos will be saved 
        dest_path = os.path.abspath("/Deepspeech/tmp")
        # Read the configuration file
        with open(args.conf_path, "r") as f:
            conf = json.load(f)
            AZURE_CONTAINER_NAME = conf["AZURE_CONTAINER_NAME"]
            AZURE_DIRECTORY_NAME = conf["AZURE_DIRECTORY_NAME"]
            AZURE_ACCOUNT_NAME = conf["AZURE_ACCOUNT_NAME"]
            AZURE_ACCOUNT_KEY = conf["AZURE_ACCOUNT_KEY"]
        
        if not os.path.exists(dest_path):
            logger.info("Creating the directory: " + dest_path)
            os.makedirs(dest_path)
        video_path = os.path.join(dest_path, args.videoid)
        if not os.path.exists(video_path):
            logger.info("Creating the directory: " + video_path)
            os.makedirs(video_path)
        
        try:
            # Initialize the AzureStorageInterface
            blob_storage = AzureStorageInterface(AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY,\
                                                 AZURE_DIRECTORY_NAME, AZURE_CONTAINER_NAME)
            if blob_storage.isVideoExist(args.videoid):
                logger.info("Downloading from blob: " + args.videoid)
                blob_storage.getVideoFilesFromAzureStorage(args.videoid, video_path)
            else:
                exit_code, output = download_youtube_video(args.videoid, dest_path)
                logger.info("Video {} downloaded with the status code {}".format(args.videoid,exit_code))
                if exit_code != 0:
                    raise Exception("Error in downloading video {} from youtube".format(args.videoid))                
        except Exception as e:
            logger.exception(e)
            raise Exception("Error in blob storage section for video {}".format(args.videoid))                
            
        # Convert mp4 to flac
        exit_code, output = mp4_to_flac(video_path)
        logger.info("Mp4 to flac exited with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in converting video {} mp4 to flac".format(args.videoid))
            
        # split on silence
        exit_code, output = split_on_silence(video_path)
        logger.info("split on silence exited with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in spliting on silence for video {}".format(args.videoid))
            
        # Use deepspeech 2
        exit_code, output = stt(video_path)
        logger.info("ds2_stt.py exited with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in ds2_stt.py for video {}".format(args.videoid))        

        # create srt
        exit_code, output = create_srt(video_path)
        logger.info("create_srt.py exited with the status code {}".format(exit_code))
        if exit_code != 0:
            raise Exception("Error in srt creation for video {}".format(args.videoid))  
        
        # save the srt to dest folder
        logger.info("Saving the srt to dest folder")
        src = video_path + os.path.sep + args.videoid +"_stt_converted.srt"
        srt_dst = dest_path + os.path.sep + args.videoid + ".en.srt"
        try:
            shutil.copy(src, srt_dst)
        except Exception as e:
            logger.exception(e)
            raise Exception("Error while saving the file to dest folder for video {}".format(args.videoid))
        
        # Push the srt to blob storage
        try:
            blob_storage.updateSRTFiles(args.videoid, srt_dst)
        except Exception as e:
            logger.exception(e)
            raise Exception("Failed to upload the srt to blob for video {}".format(args.videoid))
        
        logger.info("ASR successful".format(args.videoid))
        print("ASR successful", file=sys.stderr)
        logger.info("############################################")
        logger.info(".....Exiting stt pipeline program.....")
        logger.info("#############################################")
        print(".....Exiting stt pipeline program.....", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)
    finally:
        # cleanup
        try:
            shutil.rmtree(video_path)
        except Exception as e:
            logger.exception(e)
            pass

