#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import sys

sys.path.insert(0, '..')

import model


class Thermometer(model.devices.Thermometer):

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        return model.devices.Thermometer.Reading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)

    def proceed_telegram(self, telegram, server):
        reading = Thermometer.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        Logger.info("Thermometer reading from <{}>: {}°C, {}% humidity".format(telegram.sensor_id, reading.temperature, reading.humidity))
