#!/usr/bin/env python
# -*- coding: utf-8 -*-

from event import *

class Trigger(event.Object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    #def trigger(self, oldValue, newValue):

class ThresholdTrigger(Trigger):

    # Events
    underflow = slot()
    overflow  = slot()

    def __init__(self, name, min, max):
        super(Trigger, self).__init__(name)
        self.min = min
        self.max = max

    # Returns whether a event has been triggered
    def trigger(self, oldValue, newValue, server):
        if oldValue < self.max and newValue > self.max:
            self.overflow(server)
            return True
        elif oldValue > self.min and newValue < self.min:
            self.underflow(server)
            return True
        return False


def IntervalTrigger(Trigger):

    # Events
    enterInFromAbove = slot()
    enterInFromBelow = slot()
    aboveInterval = slot()
    belowInterval = slot()

    def __init__(self, name, min, max):
        super(Trigger, self).__init__(name)
        self.min = min
        self.max = max

    def trigger(self, oldValue, newValue, server):
        # if we were inside the interval
        if self.min <= oldValue <= self.max:
            if newValue > self.max:
                self.aboveInterval(server)
                return True
            elif newValue < self.min:
                self.belowInterval(server)
                return True
        # else if we are inside the interval now
        elif self.min <= newValue <= self.max:
            if oldValue > self.max:
                self.enterInFromAbove(server)
                return True
            if oldValue < self.min:
                self.enterInFromBelow(server)
                return True

        return False

