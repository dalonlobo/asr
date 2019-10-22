#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 15:03:24 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals
import pandas as pd
                        
import json
import urllib
import re

df = pd.read_excel("SADHGuru Channel Videos.xlsx")  

duration_list = []
for video_id in df["VideoID"]:
    api_key="xxx"
    searchUrl="https://www.googleapis.com/youtube/v3/videos?id="+video_id+"&key="+api_key+"&part=contentDetails"
    response = urllib.urlopen(searchUrl).read()
    print(response)
    data = json.loads(response)
    all_data=data['items']
    if not all_data:
        duration_list.append(None)
        continue
    contentDetails=all_data[0]['contentDetails']
    #print(contentDetails)
    duration=contentDetails['duration']
    duration_list.append(re.sub(r"[HM]", ":",duration[2:-1]))

df["Duration"] = duration_list
df.to_csv("All_videos_ids_with_duration")
