
class Sensor:
    
    def __init__(self):
        self.eventTriggers = []

class Event:

    def __init__(self):
        self.callbacks = { } # Dict of lists

    def call(self):
        pass

    def connect(self, obj, callback):
        # Obj must inherit from CallbackInterface
        obj.addEvent(self)
        if obj not in self.callbacks:
            self.callbacks[obj] = []

        self.callbacks[obj].append(callback)

    def disconnect(self, obj):
        del self.callbacks[obj]


class EventTrigger:

    def __init__(self, name):
        self.name = name
        self.events = { }

    def process(self, oldValue, newValue):
        raise NotImplemented

    #OR

    def process(self, sensor):
        raise NotImplemented


class Threshold(EventTrigger):

    def __init__(self, name):
        EventTrigger.__init__(self, name)

        self.exceedsValue = Event()

        # TODO: do this automatically (meta)
        self.events = { "Threshold1.exceedsValue", self.exceedsValue }

    def process(self, oldValue, newValue):
        

    #OR

    def process(self, sensor):
        raise NotImplemented


class CallbackInterface:

    def __init__(self):
        self.events = []

    def __del__(self):
        for e in self.events:
            e.unregister(self)

    def addEvent(self, event):
        if event not in self.events:
            self.events.append(event)


t = Temperature(...)
s = Switch(...)

t.events["threshold1.over"].connect(obj, callback)
s.events["on_click"].connect(obj, callback)
