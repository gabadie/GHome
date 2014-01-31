#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
import twisted
from datetime import datetime

sys.path.insert(0, '..')

import logger
import event

class Event(event.Object):
    name = mongoengine.StringField(required=True)
    event = event.slot()
    minutes = mongoengine.IntField(default=0, required=True)
    week_days_mask = mongoengine.IntField(default=0, required=True)

class Server(object):
    # main_server: main_server.server.MainServer
    # looping_task: mongoengine.task.LoopingCall
    # previous_minutes: int
    quantum = 10 # seconds

    def __init__(self, main_server):
        self.main_server = main_server

        now = datetime.now()
        self.previous_minutes = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds / 60

        self.looping_task = twisted.internet.task.LoopingCall(self.looping_trigger)
        self.looping_task.start(Server.quantum)

    def trigger_events(self, week_day, minutes, previous_minute):
        clock_events = Event.objects(minutes__gt=previous_minute, minutes__lte=minutes)

        for clock_event in clock_events:
            clock_event.event(self.main_server)

        return

    def looping_trigger(self):
        now = datetime.now()
        minutes = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds / 60
        week_day = now.weekday()

        if minutes < self.previous_minutes:
            # changing day
            self.trigger_events((week_day - 1) % 7, 24 * 60, self.previous_minutes)
            self.previous_minutes = -1

        self.trigger_events(week_day, minutes, self.previous_minutes)
        self.previous_minutes = minutes

        return

