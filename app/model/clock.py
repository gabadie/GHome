#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
import twisted
from datetime import datetime

sys.path.insert(0, '..')

import logger
import event

#
# week_day variable are integer, between 0 (for Monday) and 6 (for Sunday)
#

class Event(event.Eventable):
    name = mongoengine.StringField(required=True)
    event = event.slot()
    minutes = mongoengine.IntField(default=0, required=True)
    week_days_mask = mongoengine.IntField(default=0, required=True)


    def week_day_mask(self, week_day):
        assert week_day >= 0 and week_day < 7
        return (self.week_days_mask & (1 << week_day)) != 0

    def set_week_day_mask(self, week_day, boolean_mask):
        assert isinstance(boolean_mask, bool)
        assert week_day >= 0 and week_day < 7

        if boolean_mask:
            self.week_days_mask = self.week_days_mask | (1 << week_day)

        else:
            self.week_days_mask = self.week_days_mask & ~(1 << week_day)


class Server(object):
    # main_server: main_server.server.MainServer
    # looping_task: mongoengine.task.LoopingCall
    # previous_minutes: int
    quantum = 2 # seconds

    def __init__(self, main_server):
        logger.info("Clock initializing (quantum = {} seconds)".format(Server.quantum))

        self.main_server = main_server

        now = datetime.now()
        self.previous_minutes = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds / 60

        self.looping_task = twisted.internet.task.LoopingCall(self.looping_callback)
        self.looping_task.start(Server.quantum)

    def trigger_events(self, week_day, minutes, previous_minute):
        clock_events = Event.objects(minutes__gt=previous_minute, minutes__lte=minutes)

        for clock_event in clock_events:
            logger.info("Clock event '{}' triggered".format(clock_event.name))

            if clock_event.week_day_mask(week_day):
                clock_event.event(self.main_server)
        return

    def looping_callback(self):
        now = datetime.now()
        minutes = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds / 60

        if minutes == self.previous_minutes:
            return

        week_day = now.weekday()

        logger.info("Clock looping callback ({} minutes since midnight)".format(minutes))

        if minutes < self.previous_minutes:
            # changing day
            self.trigger_events((week_day - 1) % 7, 24 * 60, self.previous_minutes)
            self.previous_minutes = -1

        self.trigger_events(week_day, minutes, self.previous_minutes)
        self.previous_minutes = minutes

        return

