#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

class Reading(object):
    def __init__(self):
        self.device = None
    
    def save(self):
        #TODO: database write access
        raise NotImplemented()
    
    