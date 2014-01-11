#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import core
import devices


class ThermometerReading(core.Reading):
    temperature = mongoengine.FloatField(required=True)
    humidity = mongoengine.FloatField(required=True)
