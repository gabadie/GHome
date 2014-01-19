#!/usr/bin/env python
# -*- coding: utf-8 -*-

import event
import mongoengine


class FakeDevice0(event.Object):
    event0 = mongoengine.ReferenceField(event.Event, required=True)
    name = mongoengine.StringField()
    received_event = mongoengine.BooleanField(default=False)

    def __str__(self):
        return self.name

    @staticmethod
    def create(name):
        o = FakeDevice0(name=name)
        o.event0 = event.Event()
        o.event0.save()
        return o

    def event_callback(self):
        self.received_event = True
        self.save()


class FakeDevice1(event.Object):
    devices = mongoengine.ListField(mongoengine.ReferenceField(FakeDevice0))


def test_events_list():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    obj0 = FakeDevice0.create(name="hello")

    obj1 = FakeDevice1()
    obj1.devices = [obj0]

    assert 'event0' in obj0.events
    assert 'hello.event0' in obj1.events

    assert obj0.events['event0'] == obj0.event0

def test_callbacks():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    a = FakeDevice0.create(name="A")
    a.save()

    b = FakeDevice0.create(name="B")
    b.save()

    assert a.received_event == False
    assert b.received_event == False

    a.event0.connect(b, 'event_callback')

    assert a.received_event == False
    assert b.received_event == False

    a.event0.trigger()

    assert a.received_event == False
    assert b.received_event == False

    b.reload()
    assert b.received_event == True


if __name__ == "__main__":
    test_events_list()
    test_callbacks()
