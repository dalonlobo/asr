#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:13:22 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import youtube_dl
import logging

import pandas as pd

from utils import run_command
from youtube_dl.utils import DownloadError

logger = logging.getLogger("__main__")

def _get_videoid_from_URL(youtube_link):
    " Returns the video id"
    # https://www.youtube.com/watch?v=UzxYlbK2c7E

    if '?v=' not in youtube_link:
        return None
    index = youtube_link.find('?v=')
    return youtube_link[index + 3:]

def _get_videoids_from_playlists(youtube_link):
    """
    Youtube link can be a playlist. This will return all the videoids,
    from that playlist
    """
    # Options for youtube-dl
    # https://github.com/rg3/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312
    ydl_opts = {'outtmpl': '%(id)s%(ext)s'}
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    
    with ydl:
        result = ydl.extract_info(
            youtube_link,
            download=False # We just want to extract the info
        )    
        
    allVideoLinks = []
    allVideoIDs = []
    # Return none if there are no videos
    if result == None:
        return (None, None)
    
    if 'entries' in result:
        videoentries = result['entries']
        print('length of video object is : ', len(videoentries))

        for eachentry in videoentries:
            if eachentry == None:
                continue

            videolink = eachentry['webpage_url']
            print('Entry is : ', videolink)
            allVideoLinks.append(videolink)
            videoid = _get_videoid_from_URL(videolink)
            allVideoIDs.append(videoid)
    else:
        videoentry = result
        videolink = videoentry['webpage_url']
        allVideoLinks.append(videolink)
        videoid = _get_videoid_from_URL(videolink)
        allVideoIDs.append(videoid)

    return (allVideoLinks, allVideoIDs)

def download_videos(destpath, allvideoids):
    """
    Downloads all the videos in the allvideosids list to the
    destination directory.
    """
    try:
        for index, videoid in enumerate(allvideoids):
            op_path = os.path.join(destpath, videoid)
            if not os.path.exists(op_path):
                os.makedirs(op_path)

            cmd = 'youtube-dl' + " -o '" + os.path.join(op_path, videoid) +\
                    ".%(ext)s' -f mp4 --write-sub --sub-lang 'en' --convert-subs " + \
                    "srt --write-auto-sub --write-info-json --prefer-ffmpeg " + \
                    "https://www.youtube.com/watch?v=" + videoid
            logger.debug('Built cmd: ' + cmd)
            run_command(cmd)
            logger.info('Video {} downloaded successfully'.format(videoid))
    except DownloadError as e:
        logger.exception(e)
        logger.error("Could not download the following videos:")
        logger.error(allvideoids)
        pass



def download_all_videos(destpath, df_to_download):
    """
    This will download all the videos which have transcriptions
    into the destination path.
    There is no check for if the videos have transcripts, make sure to send the
    list of videos/playlists with transcripts.
    Columns of the dataframe should be : VideoID,	Link, 	Transcribed
    """
    try:
        videopath = os.path.join(destpath)
        count = 0
        for youtube_link in df_to_download.Link:
            logger.info("Processing the link: " + youtube_link)
            (allvideolinks, allvideoids) = _get_videoids_from_playlists(youtube_link)
            
            if allvideolinks == None:
                continue
            count += len(allvideolinks)
            download_videos(videopath, allvideoids)
        print("Successfully downloaded all the videos", file=sys.stderr)
        logger.info("Successfully downloaded {} videos".format(count))
        return True
    except Exception as e:
        logger.exception(e)
        return False

if __name__ == "__main__":
    """
    This script will download all videos in the excel file
    Columns of excel file should be VideoID,	Link, 	Transcribed
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
    parser = argparse.ArgumentParser(description="Download videos from youtube")
    parser.add_argument('--vidlist', type=str,  
                        help='Path to the excel file containing list of videos to download')
    parser.add_argument('--destpath', type=str,  
                        help='Path to store the video files')
    args = parser.parse_args()
    # Path to the destination folder, where videos will be saved 
    destpath = os.path.abspath(args.destpath)
    # path to excel  file containing the list of videos to download
    vidlist = os.path.abspath(args.vidlist)    
    # Create the destination folder if it does not exist
    if not os.path.exists(destpath):
        logger.info("Creating the directory: " + destpath)
        os.makedirs(destpath)
        
    # Read the videos list from excel file
    # Columns are VideoID,	Link, 	Transcribed
    df_to_download = pd.read_excel(vidlist)
    logger.debug("List of videos that will be downloaded: \n")
    logger.debug(df_to_download.Link)
    # Download all the videos in the list to the destination folder
    download_all_videos(destpath, df_to_download)
    logger.info("All videos downloaded successfully")
    print("All videos downloaded successfully", file=sys.stderr)
    logger.info("#########################")
    logger.info(".....Exiting program.....")
    logger.info("#########################")
    print(".....Exiting program.....", file=sys.stderr)
