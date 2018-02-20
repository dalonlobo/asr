#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:12:20 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, \
                        print_function, unicode_literals
import sys
import json

if __name__ == "__main__":
    with open("job.log", "a") as op:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)
            
        if jobs["status"] == "0":
            print("Running the job with id ", file=op)