import mongoengine
from event import Eventable, slot

class Trigger(Eventable):
    name = mongoengine.StringField(required=True)

    def __str__(self):
        return self.name.encode('utf-8')

    # Returns whether a event has been triggered
    def trigger(self, oldValue, newValue, server):
        raise NotImplemented


class BinaryTrigger(Trigger):
    # Events
    open  = slot()
    close = slot()

    # Returns whether a event has been triggered
    def trigger(self, oldValue, newValue, server):
        if oldValue != newValue:
            if oldValue == False:
                self.open(server)
            else:
                self.close(server)


class ThresholdTrigger(Trigger):

    min = mongoengine.fields.IntField(required=True)
    max = mongoengine.fields.IntField(required=True)

    # Events
    underflow = slot()
    overflow  = slot()

    # Returns whether a event has been triggered
    def trigger(self, oldValue, newValue, server):
        if oldValue < self.max and newValue > self.max:
            print "OVERFLOW"
            self.overflow(server)
            return True
        elif oldValue > self.min and newValue < self.min:
            print "UNDERFLOW"
            self.underflow(server)
            return True
        return False


class IntervalTrigger(Trigger):

    min = mongoengine.fields.IntField(required=True)
    max = mongoengine.fields.IntField(required=True)

    # Events
    enterInFromAbove = slot()
    enterInFromBelow = slot()
    aboveInterval = slot()
    belowInterval = slot()

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


