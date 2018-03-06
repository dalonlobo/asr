#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:41:20 2018

@author: dalonlobo
"""
from __future__ import absolute_import, print_function, division, unicode_literals

import sys
import re

from n2w import convert

def process_line(line):
    """ Preprocessing of the text data:
            :1: Characters not in [A-Za-z0-9\s'] removed
            :2: Arabic numbers are converted to English numbers 
                like 1000 to one thousand
            :3: Repeated whitespace characters are squeezed to 
                one and the beginning whitespace characters are removed
            :4: All characters are converted to lowercase
    """
    # Splitting will remove repeated white spaces
    line = re.sub(r"[^a-zA-z0-9\s]", "", line).split()
    for index, word in enumerate(line):
        line[index] = line[index].lower()
        if word.isdigit():
            try:
                line[index] = convert(int(word))
            except:
                pass
    return " ".join(line) + "\n"
    

if __name__ == "__main__":
        BATCH_SIZE = 5000
        with open(sys.argv[1], "r") as f1, open("en.00.deduped.processed","a") as f2:
            temp = []
            for line in f1:
                temp.append(process_line(line))
                if len(temp) == BATCH_SIZE:
                    f2.writelines(temp)
                    temp = []
            f2.writelines(temp)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            