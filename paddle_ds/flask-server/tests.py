#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 1 11:13:22 2018

@author: dalonlobo
"""
import os
import app
import unittest
import json
import tempfile

class ServerTestCase(unittest.TestCase):
    
    document_id = ''

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    def test_empty_request(self):
        rv = self.app.get('/')
        assert b'To make request use: /asr/api/v1.0/make_request' in rv.data

    def test_make_request(self):
        rv = self.app.get('/asr/api/v1.0/make_request')
        # method not allowed
        assert rv.status_code == 405
        rv = self.app.post('/asr/api/v1.0/make_request')
        # post request without json
        assert rv.status_code == 400

if __name__ == '__main__':
    unittest.main()
