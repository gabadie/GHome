#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import protocol

sys.path.insert(0, '..')

import telegram
import model.devices
import logger


class Sensor(model.devices.Sensor):
    ignored = mongoengine.BooleanField(default=True)

    def process_telegram(self, telegram, server):
        raise NotImplementedError


# Sensors
class Thermometer(model.devices.Thermometer):
    
    @staticmethod
    def generate_telegram(sensor_id, temperature, humidity):
        data_bytes = [0x0 for i in xrange(4)]
        data_bytes[1] = int(humidity * 250 / 100)
        data_bytes[2] = int(temperature * 250 / 40)
        return telegram.from_sensor_data_bytes(sensor_id=sensor_id, data_bytes=data_bytes)

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        return model.devices.Thermometer.Reading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)

    def process_telegram(self, telegram, server):
        reading = Thermometer.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        logger.info("EnOcean thermometer reading: temperature=" + str(reading.temperature) + "C, humidity=" + str(reading.humidity) + "%")

        
class Switch(model.devices.Switch):
    UNKNOWN, TOP, BOTTOM, RIGHT, LEFT = range(5)
    
    @staticmethod
    def generate_telegram(sensor_id, side, direction, pressed):
        data_bytes = [0x0 for i in xrange(4)]
        
        if not pressed:
            side = UNKNOWN
            direction = UNKNOWN
        else:
            data_bytes[0] = data_bytes[0] | 0x01
            
        if side == Switch.RIGHT:
            data_bytes[0] = data_bytes[0] | 0x04
            
        if direction == Switch.TOP:
            data_bytes[0] = data_bytes[0] | 0x02
        
        return telegram.from_sensor_data_bytes(sensor_id=sensor_id, data_bytes=data_bytes)

    @staticmethod
    def reading_from_data_bytes(switch, data_bytes):
        if data_bytes[0] & 0x01 == 0:
            side = Switch.UNKNOWN
            direction = Switch.UNKNOWN
            pressed = False
            switch.top_right = False
            switch.top_left = False
            switch.bottom_right = False
            switch.bottom_left = False
        else:
            if (data_bytes[0] & 0x04) == 0x04:
                side = Switch.RIGHT
            else:
                side = Switch.LEFT
                
            if (data_bytes[0] & 0x02) == 0x02:
                direction = Switch.TOP
                if side == Switch.RIGHT:
                    switch.top_right = not switch.top_right
                else:
                    switch.top_left = not switch.top_left
            else:
                direction = Switch.BOTTOM
                if side == Switch.RIGHT:
                    switch.bottom_right = not switch.bottom_right
                else:
                    switch.bottom_left = not switch.bottom_left
                
            pressed = True
            
        return model.devices.Switch.Reading(device=switch, side=side, direction=direction, pressed=pressed)

    def process_telegram(self, telegram, server):
        reading = Switch.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()
        
        self.save()


class WindowContact(model.devices.WindowContact):
    
    @staticmethod
    def generate_telegram(sensor_id, open):
        data_bytes = [0x0 for i in xrange(4)]
        if not open:
            data_bytes[3] = 0x01
        return telegram.from_sensor_data_bytes(sensor_id=sensor_id, data_bytes=data_bytes)

    @staticmethod
    def reading_from_data_bytes(windowContact, data_bytes):
        windowContact.open = ((data_bytes[3] & 0x01) == 0)

        return model.devices.WindowContact.Reading(device=windowContact, open=windowContact.open)
        
    def process_telegram(self, telegram, server):
        reading = WindowContact.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()
        logger.info("EnOcean window contactor reading: open=" + str(reading.open))

        
class LightMovementSensor(model.devices.LightMovementSensor):
    
    @staticmethod
    def generate_telegram(sensor_id, voltage, brightness, movement):
        data_bytes = [0x0 for i in xrange(4)]
        data_bytes[0] = int(voltage * 255 / 5.1)
        data_bytes[1] = int(brightness * 255 / 510)
        if not movement:
            data_bytes[3] = 0x01
        return telegram.from_sensor_data_bytes(sensor_id=sensor_id, data_bytes=data_bytes)

    @staticmethod
    def reading_from_data_bytes(lightMovementSensor, data_bytes):
        movement = ((data_bytes[3] & 0x01) == 0x00)
        return model.devices.LightMovementSensor.Reading(device=lightMovementSensor, 
            voltage=(data_bytes[0] * 5.1 / 255.0), brightness=data_bytes[1] * 510 / 255.0, movement=movement)

    def process_telegram(self, telegram, server):
        reading = LightMovementSensor.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()
        logger.info("EnOcean light and movement sensor reading: voltage=" + str(reading.voltage) + "V, brightness=" + str(reading.brightness) + "Lux, movement=" + str(reading.movement))


# Actuators
class Lamp(model.devices.Lamp):

    def activate(self, sensor):
        self.turned_on = not self.turned_on
        logger.info("Lamp #{} state changed. turned_on = {}".format(self.device_id, self.turned_on))

        self.save()


def from_telegram(telegram):
    if telegram.device_type == telegram.Telegram.SRW01:
        return WindowContactor(device_id=telegram.sensor_id)
    
    if telegram.device_type == telegram.Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)
    
    if telegram.device_type == telegram.Telegram.SR_MDS:
        return LightMovementSensor(device_id=telegram.sensor_id)
    
    return None