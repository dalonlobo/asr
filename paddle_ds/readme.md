# Instructions

**Steps to use this repo**
-> Download the videos using                        download_from_youtube.py
-> Convert srt to text for                          comparison using srt_to_textfile.py
-> Convert mp4 to wav using                         mp4_to_wav.py
-> Split the wav on silence using                   split_on_silence.py
-> Call cris api on all split files                 ds2_stt.py
-> To create srt files of the output                create_srt.py

**Steps to run the entire pipeline**
-> python stt_pipeline.py --videoid xxxxx

**Steps to insert the request into cosmosdb**
-> python request_stt.py --conf_path config.json --videoid U41RQaZ1Uqg --storage_type youtube
