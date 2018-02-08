# coding: utf-8

import os
import argparse
import base64
import json
import time
import sys
import re

#from googleapiclient import discovery
#import httplib2
#from oauth2client.client import GoogleCredentials

import math 
import numpy as np
import os
import tempfile as tmpf
import shutil
import subprocess as sp

import client as ck
import pandas as pd

from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import detect_nonsilent 

from websocket import create_connection

# #####Start of code based on the Google api sample######
# DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
#                  'version={apiVersion}')

# def get_speech_service():
#     credentials = GoogleCredentials.get_application_default().create_scoped(
#         ['https://www.googleapis.com/auth/cloud-platform'])
#     http = httplib2.Http()
#     credentials.authorize(http)
#     return discovery.build(
#         'speech', 'v1beta1', http=http, discoveryServiceUrl=DISCOVERY_URL)

# def processResponse(response):
#     output = ''
#     if ("results" in response.keys()) \
# 	and (len(response['results']) != 0) \
# 	and ("alternatives" in response['results'][0].keys()) \
# 	and (len(response['results'][0]['alternatives']) != 0) \
# 	and ("transcript" in response['results'][0]['alternatives'][0].keys()):
# 	output = response['results'][0]['alternatives'][0]['transcript']
#     else:
# 	print "Empty ASR output: ",response	
#     return output

# def transcribe_chunk(fpath,fr):
#     #os.system('export GOOGLE_APPLICATION_CREDENTIALS='+gcloud_credentials_fpath)
#     #execute_command(command_to_export(gcloud_credentials_fpath))
#     with open(fpath, 'rb') as speech:
#         speech_content = base64.b64encode(speech.read()) # Base64 encode the binary audio file for inclusion in the JSON request.
    
#     service = get_speech_service()
#     service_request = service.speech().syncrecognize(
#         body={
#             'config': {
#                 'encoding': 'flac',  # raw 16-bit signed LE samples
#                 'sampleRate': fr,  # 16 khz.
#                 'languageCode': 'en-US',  # a BCP-47 language tag
#             },
#             'audio': {
#                 'content': speech_content.decode('UTF-8')
#                 }
#             })
#     response = service_request.execute()
#     output_result = processResponse(response)
#     return output_result 
# #####end of code based on the Google api sample######

## list_of_ws = ["ws://swordfish:9990/client/ws"]
list_of_ws = []
# def is_docker_free(ws):
#     tmp_dir = tmpf.mkdtemp()
#     fpath= tmp_dir+os.sep+"temp_docker"
#     pid = execute_command(cmd_to_check_if_docker_free(ws,fpath))
#     execute_command(cmd_to_kill_pid(pid))
#     fp = open(fpath)
#     content = fp.read()
#     print "content: ",content
#     reg_exp = r'("num_workers_available": )([0-9]+)'
#     is_free = False
#     search_obj = re.search(reg_exp,content)
#     if search_obj:
#         if search_obj.group(2) == 0:
#             is_free = True
#     else:
#         raise Exception("Unable to determine if the kaldi docker is free.")
#     #shutil.rmtree(tmp_dir)
#     return is_free

def is_docker_free(ws):
	wsc = create_connection(ws)
	result =  wsc.recv()	
	reg_exp = '("num_workers_available": )([0-9]+)'
	is_free = False
	search_obj = re.search(reg_exp,result)
	if search_obj:
		if int(search_obj.group(2)) > 0:
			is_free = True
	else:
		raise Exception("Unable to determine if the kaldi docker is free.")
	return is_free

def transcribe_chunk(fpath_in,fr):
	try:
		print "Connecting to Kaldi..."
		for ws in list_of_ws:
			print "Checking if free: ",ws+"/status"
			if is_docker_free(ws+"/status"):
				print "Its free."
				transcript = ck.generate_transcript(fpath_in,uri=ws+"/speech",rate=fr,content_type='')
				return transcript
			else:
				print "Its NOT free."
		print "No Kaldi Docker is free."
		raise Exception('No Kaldi Docker is free.')
	except Exception as e:
		raise e
	# tmp_dir = tmpf.mkdtemp()
	# fpath_out = tmp_dir+'/kaldi_tmp'
	# execute_command(command_to_run_kaldi_transcription(fpath_in,fpath_out))
	# fp = open(fpath_out)
	# result = fp.read()
	# shutil.rmtree(tmp_dir)
	# return result

def get_formatted_time(time_ms):
    a_min = 60 #secs
    a_hour = 60 #mins
    temp = time_ms / 1000
    time_secs = temp % a_min
    temp /= a_min
    time_mins = temp % a_hour
    temp /= a_hour
    time_hrs = temp
    return str(time_hrs).zfill(2)+":"+str(time_mins).zfill(2)+":"+str(time_secs).zfill(2)+",000"

def update_srt_file(chunk_transcript,i,start,end,srt_file_path):
    srt_file_path.write(i)
    srt_file_path.write("\n")
    #time
    start_ftime = get_formatted_time(start)
    end_ftime = get_formatted_time(end)
    srt_file_path.write(start_ftime+" --> "+end_ftime)
    srt_file_path.write("\n")
    #text
    srt_file_path.write(chunk_transcript)
    srt_file_path.write("\n")
    srt_file_path.write("\n")

def command_to_convert_mp4_to_mp3(fpath_in,fpath_out):
    cmd = "ffmpeg -i "+fpath_in+" -ac 1 -- "+fpath_out
    return cmd

# def command_to_run_kaldi_transcription(fpath_in,fpath_out):
# 	cmd = "python client_kaldi.py -u ws://localhost:9990/client/ws/speech -r 32000 "+fpath_in+" > "+fpath_out
# 	return cmd

def cmd_to_check_if_docker_free(ws,fpath):
    cmd = 'wscat -c '+ws+' 1> '+fpath
    return cmd

def cmd_to_kill_pid(pid):
	cmd = 'kill -INT '+str(pid)
	return cmd

def execute_command(command):
    p = sp.Popen(command,
                 bufsize=2048,
                 shell=True,
                 stdin=sp.PIPE,
                 stdout=sp.PIPE,
                 stderr=sp.PIPE,
                 close_fds=(sys.platform != 'win32'))
    output = p.communicate()
    print("Executed : " + command)
    return p.pid

#generates srt file for the given mp4 file
def generate_srt(fpath, tmp_dir, kaldi_ws="ws://swordfish:9990/client/ws", part_len=5000):
        list_of_ws.append(kaldi_ws)
	max_retries = 10
	wait_time = 60 #secs
	try:
	    #load the input mp4 file
	    #full_sound_wav = AudioSegment.from_file(fpath, format="mp4")
	    #temp dir to hold all chunks 
	    #export mp4 to flac
	    temp_fpath_splits = fpath.split(".")[0].split(os.sep)
	    flac_file_name = temp_fpath_splits[len(temp_fpath_splits)-1]+".mp3"
	    flac_file_path = tmp_dir+os.sep+flac_file_name
	    #full_sound_wav.export(flac_file_path,format="flac")
	    execute_command(command_to_convert_mp4_to_mp3(fpath,flac_file_path))
	    #load the flac file
	    full_sound_flac = AudioSegment.from_file(flac_file_path, format="mp3")
	    full_sound_flac_len = full_sound_flac.__len__()

            full_audio_wav = normalize(full_sound_flac)
            loudness_ms_list = [] # Save the audio levels of all the chunks
            for ms_chunk in full_audio_wav:
                loudness_ms_list.append(round(ms_chunk.dBFS))
            print "Audio levels are recorded"

            # Using pandas df for easier manipulation
            df = pd.DataFrame(loudness_ms_list)
            df[0] = df[df[0] != float("-inf")] # Remove the very low levels
            st = df[0].mean()
            print "Mean Audo level is", st
            st = st if st < -16 else -16 # Because -16db is default

            # Splits the audio if silence duration is MSL long
            MSL = 500 # minimum silence length in ms

            not_silence_ranges = detect_nonsilent(full_sound_flac, min_silence_len=MSL, silence_thresh=st)
            min_non_silent_part = 1 * part_len
            max_non_silent_part = 6 * part_len
           
            # Split large non silent audio ranges  
            split_ranges = []
            for start_i, end_i in not_silence_ranges:
                non_silent_part = end_i - start_i
                num_non_silent_parts = (non_silent_part + max_non_silent_part - 1)/max_non_silent_part
                start = start_i
                for i in np.arange(num_non_silent_parts):
                    end = start + max_non_silent_part
                    end = end if end < end_i else end_i
                    print "Start split non silent", start, "End split non silent", end
                    split_ranges.append([start, end])
                    start = end
 
            # Merge small non silent audio ranges 
            merged_ranges = []
            merged_start = 0
            non_silent_part = min_non_silent_part
            for start_i, end_i in split_ranges:
                non_silent_part = end_i - merged_start
                if non_silent_part >= min_non_silent_part:
                    merged_end = end_i + MSL/2
                    merged_ranges.append([merged_start, merged_end])
                    print "Start merged non silent", merged_start , "End merged non silent" , merged_end
                    merged_start = merged_end
            if non_silent_part < min_non_silent_part:
                merged_end = end_i + MSL/2
                merged_ranges.append([merged_start, merged_end])
                print "Start merged non silent", merged_start , "End merged non silent" , merged_end

            # Handle the case when there are no non silent audio ranges
            if not merged_ranges:
                num_silent_parts = (full_sound_flac_len + part_len - 1)/part_len
                start = 0
                for i in np.arange(num_silent_parts):
                    end = start + part_len
                    end = end if end < full_sound_flac_len else full_sound_flac_len
                    print "Start split silent", start, "End split silent", end
                    merged_ranges.append([start, end])
                    start = end
 
	    # split chunks, generate transcript and update srt file
	    srt_file_path = fpath.split(".")[0]+".srt"
	    srt_file = open(srt_file_path,"w")
            i = 0
            for start_i, end_i in merged_ranges:
			retry_count = 0
			print i, "Start ", start_i, "End ", end_i
                        start = start_i
                        end = end_i 
                        if end > full_sound_flac_len:
                           end = full_sound_flac_len
			chunk_transcript = ''
			cur_chunk_fname = "chunk_"+str(start)+"_"+str(end)+".mp3"
			cur_chunk_fpath = tmp_dir + "/" + cur_chunk_fname
			print "Processing: ",cur_chunk_fpath
			full_sound_flac[start:end].export(cur_chunk_fpath,format="mp3")
			#transcribe this chunk
			fr = full_sound_flac.frame_rate
			while True:
				try:
					stime = time.time()
					chunk_transcript = transcribe_chunk(cur_chunk_fpath,fr)
					etime = time.time()
					print "Took ",(etime-stime)," secs."
					#print "chunk_transcript: ",chunk_transcript
				except Exception as e:
					print e
					retry_count+=1
					if retry_count < max_retries:
						time.sleep(wait_time)
						print "Waited "+str(wait_time)+" secs. Retrying...(",str(retry_count),")"
						continue
				break 	
			#update the srt file
			update_srt_file(chunk_transcript,str(i+1),start,end,srt_file)
			#update indices
                        i = i + 1
	except Exception as e:
	    print "Fatal Error occurred."    
	    print e
	finally:
	    #cleaning up
	    srt_file.close()

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'Usage: python kaldi_asr.py path_to_mp4'
		sys.exit(0)
	fpath = sys.argv[1]
	tmp_dir = tmpf.mkdtemp()
	generate_srt(fpath, tmp_dir)
        #cleaning up
	shutil.rmtree(tmp_dir)

