#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine


class Device(mongoengine.Document):
    device_id = mongoengine.StringField(required=True, unique=True)
    name = mongoengine.StringField()

    meta = {'allow_inheritance': True}


class Reading(mongoengine.Document):
    device = mongoengine.ReferenceField(Device, required=True)

    meta = {'allow_inheritance': True}
