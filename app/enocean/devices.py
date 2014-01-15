#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import protocol

sys.path.insert(0, '..')

from telegram import Telegram
import model.devices
import logger


class Sensor(model.devices.Sensor):
    ignored = mongoengine.BooleanField(default=True)

    def process_telegram(self, telegram, server):
        raise NotImplementedError

# Sensors
class Thermometer(Sensor, model.devices.Thermometer):
    
    @staticmethod
    def generate_telegram(sensor_id, temperature, humidity):
        data_bytes = [0x0 for i in xrange(4)]
        data_bytes[1] = humidity * 250 / 100.0
        data_bytes[2] = temperature * 250 / 40.0
        return telegram.from_sensor_data_bytes(sensor_id=sensor_id, data_bytes=data_bytes)

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        return model.devices.Thermometer.Reading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)

    def process_telegram(self, telegram, server):
        reading = Thermometer.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        logger.info("EnOcean thermometer reading: temperature=" + str(reading.temperature) + "C, humidity=" + str(reading.humidity) + "%")

class Switch(Sensor, model.devices.Switch):
    UNKNOWN, UP, DOWN, RIGHT, LEFT = range(5)
    
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
            
        if direction == Switch.UP:
            data_bytes[0] = data_bytes[0] | 0x02
        
        return telegram.from_sensor_data_bytes(sensor_id=sensor_id, data_bytes=data_bytes)

    @staticmethod
    def reading_from_data_bytes(switch, data_bytes):
        if data_bytes[0] & 0x01 == 0:
            side = Switch.UNKNOWN
            direction = Switch.UNKNOWN
            pressed = False
        else:
            if (data_bytes[0] & 0x04) >> 1 == 1:
                side = Switch.RIGHT
            else:
                side = Switch.LEFT
                
            if (data_bytes[0] & 0x02) >> 1 == 1:
                direction = Switch.UP
                if side == Switch.RIGHT:
                    switch.topRight = not switch.topRight
                else:
                    switch.topLeft = not switch.topLeft
            else:
                direction = Switch.DOWN
                if side == Switch.RIGHT:
                    switch.bottomRight = not switch.bottomRight
                else:
                    switch.bottomLeft = not switch.bottomLeft
                
            pressed = True
            
        return model.devices.Switch.Reading(device=switch, side=self.side, direction=self.direction, pressed=self.pressed)

    def process_telegram(self, telegram, server):
        reading = Switch.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()
        
        self.save()


class WindowContact(Sensor, model.devices.WindowContact):
    
    @staticmethod
    def generate_telegram(sensor_id, open):
        data_bytes = [0x0 for i in xrange(4)]
        if not open:
            data_bytes[3] = 0x01
        return telegram.from_sensor_data_bytes(sensor_id=sensor_id, data_bytes=data_bytes)

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        self.open = (self.data_bytes[3] & 0x01) == 0

        return model.devices.WindowContact.Reading(device=windowContact, open=self.open)


class LightMovementSensor(model.devices.LightMovementSensor):
    
    @staticmethod
    def generate_telegram(sensor_id, voltage, brightness, movement):
        data_bytes = [0x0 for i in xrange(4)]
        data_bytes[0] = voltage * 255 / 5.12
        data_bytes[1] = brightness * 255 / 512.0
        if movement:
            data_bytes[3] = 0x02
        return telegram.from_sensor_data_bytes(sensor_id=sensor_id, data_bytes=data_bytes)

    @staticmethod
    def reading_from_data_bytes(lightMovementSensor, data_bytes):
        movement = (self.data_bytes[3] & 0x02) >> 1
        if movement == 0:
            movement = True
        else:
            movement = False
        return model.devices.LightMovementSensor.Reading(device=lightMovementSensor, 
            voltage=data_bytes[0] * 5.12 / 255.0, brightness=data_bytes[1] * 512 / 255.0, movement=movement)

    def process_telegram(self, telegram, server):
        reading = LightMovementSensor.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()
        logger.info("EnOcean light and movement sensor reading: voltage=" + str(reading.voltage) + "V, brightness=" + str(reading.brightness) + "Lux, movement=" + str(reading.movement))


# Actuators
class Lamp(model.devices.Actuator, model.devices.Lamp):

    def activate(self, sensor):
        self.turned_on = not self.turned_on
        logger.info("Lamp #{} state changed. turned_on = {}".format(self.device_id, self.turned_on))

        self.save()


def from_telegram(telegram):
    if telegram.device_type == Telegram.SRW01:
        return WindowContactor(device_id=telegram.sensor_id)
    
    if telegram.device_type == Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)
    
    if telegram.device_type == Telegram.SR_MDS:
        return LightMovementSensor(device_id=telegram.sensor_id)
    
    return None