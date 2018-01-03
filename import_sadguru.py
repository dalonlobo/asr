#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 15:06:43 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import os
import argparse
import youtube_dl
import logging
import progressbar

import pandas as pd

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

def run_command(cmd):
    try:
        os.system(cmd)
    except Exception as e:
        logging.exception(e)
        print('exception caught ', str(e))

def download_videos(destpath, allvideoids):
    for index, videoid in enumerate(allvideoids):
        op_path = os.path.join(destpath, videoid)
        if not os.path.exists(op_path):
            os.makedirs(op_path)

        cmd = 'youtube-dl' + " -o '" + os.path.join(op_path, videoid) +\
                ".%(ext)s' -f mp4 --write-sub --sub-lang 'en' --convert-subs " + \
                "srt --write-auto-sub --write-info-json --prefer-ffmpeg " + \
                "https://www.youtube.com/watch?v=" + videoid
        print('Built cmd: ', cmd)
        run_command(cmd)
        print('Download complete')



def _download_all_videos(destpath, df_to_download):
    """
    This will download all the videos which have trancriptions
    into the destination path
    """
    for youtube_link in df_to_download.Link:
        logging.info("Processing the link: " + youtube_link)
        (allvideolinks, allvideoids) = _get_videoids_from_playlists(youtube_link)
        
        if allvideolinks == None:
            continue

        download_videos(destpath, allvideoids)

if __name__ == "__main__":
    logs_path = os.path.basename(__file__) + ".logs"
    logging.basicConfig(filename=logs_path,
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    parser = argparse.ArgumentParser(description="""
                                     This script will import sadguru videos and preprocess them, 
                                     so that you can train deepspeech model""")
    parser.add_argument('--vidlist', type=str,  
                        help='Path to the excel file containing list of videos to download')
    parser.add_argument('--destpath', type=str,  
                        help='Path to store the video files')
    args = parser.parse_args(["--vidlist", "SADHGuru Channel Videos.xlsx", "--destpath", "tmp"])
    # Path to the destination folder, where videos will be saved 
    destpath = os.path.abspath(args.destpath)
    # path to excel  file containing the list of videos to download
    vidlist = os.path.abspath(args.vidlist)
    
    # Create the destination folder if it does not exist
    if not os.path.exists(destpath):
        os.makedirs(destpath)
        
    # Read the videos list from excel file
    # Columns are VideoID,	Link, 	Transcribed
    df_to_download = pd.read_excel(vidlist)
    
    # Retain only the videos which have transcription
    df_to_download = df_to_download[df_to_download.Transcribed == 1]
    
    _download_all_videos(destpath, df_to_download)
    
    
    
    
    
    
    
    
    
    
