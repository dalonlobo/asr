#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 22:02:14 2018

@author: dalonlobo
"""
sdf = df_to_download.sort_values("VideoID")

df_100 = sdf.iloc[175:201,:]

all_samples_path = os.path.join(destpath, "25_samples")
if not os.path.exists(all_samples_path):
    os.makedirs(all_samples_path)
  
from distutils.dir_util import copy_tree
    
for dirs in df_100["VideoID"]:
    directory = os.path.join(videospath, dirs)
    if not os.path.isdir(directory):
        continue # Do nothing if its not a directory
    print(os.path.join(directory, "samples"))
    print(all_samples_path)
    copy_tree(os.path.join(directory, "samples"), all_samples_path)
    
    
# Path to txt files
csv_files_path = os.path.join(destpath, "Videos")
csv_files_list = glob.glob(csv_files_path + "/*.txt")

list_175 = [x for x in csv_files_list if x.split('/')[-1].replace('_data.txt','') in list(df_100["VideoID"])]


# Read the first dataframe
df = pd.read_csv(list_175[0], sep=b'\t', header=None, \
                 names=["wav_filename", "transcript"])
# Append to the main dataframe
for csv_file in list_175[1:]:
    temp_df = pd.read_csv(csv_file, sep=b'\t', header=None, \
                 names=["wav_filename", "transcript"])
    df = df.append(temp_df)

# Drop the null values
df.dropna(inplace=True)
df.to_csv(os.path.join(destpath, "azure-test-25.txt"), index=False,\
          header=False, sep=b'\t')