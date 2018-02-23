#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 15:30:30 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals

import os
import sys
import argparse
import logging
import pysrt
import glob
import text

logger = logging.getLogger("__main__")

def compare_wer(ref, hyp):
    with open(ref, "r") as ref, open(hyp, "r") as hyp:
        return text.wer(ref.read(), hyp.read())

if __name__ == "__main__":
    """
    Compare 2 file and return the wer's
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
    parser = argparse.ArgumentParser(description="wers calculator")
    parser.add_argument('--ref', type=str,  
                        help='Path to ref')
    parser.add_argument('--hyp', type=str,  
                        help='Path to hyp')
    # Remove the below line 
#    args = parser.parse_args(["--ref", "/home/dalonlobo/deepspeech_models/asr/cris_demo/Videos/XtiYlNM9jRc/XtiYlNM9jRc.en.srt.ref.txt",
#                              "--hyp", "/home/dalonlobo/deepspeech_models/asr/cris_demo/Videos/XtiYlNM9jRc/hyp.txt"])
    # Uncomment the below line
    args = parser.parse_args()
    ref = os.path.abspath(args.ref)
    hyp = os.path.abspath(args.hyp)
    logger.debug("Reading the files: \n")
    results = compare_wer(ref, hyp)
    print("Results: ", results)
    logger.info("Results")
    logger.info(results)
    logger.info("#########################")
    logger.info(".....Exiting program.....")
    logger.info("#########################")
    print(".....Exiting program.....", file=sys.stderr)

