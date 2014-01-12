#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core
import mongoengine


class Thermometer(object):
    class Reading(core.Reading):
        temperature = mongoengine.FloatField(required=True)
        humidity = mongoengine.FloatField(required=True)
