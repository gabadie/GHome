#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

class Reading:
    def __init__(self):
        #TODO for database implementation => device in constructor
        self.device = None
    
    def save(self):
        #TODO: database write access
        raise NotImplemented()
    
    