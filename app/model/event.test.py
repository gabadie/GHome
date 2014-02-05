#!/usr/bin/env python
# -*- coding: utf-8 -*-

import event
import mongoengine


class FakeDevice0(event.Eventable):
    event0 = event.slot()
    name = mongoengine.StringField()
    received_event = mongoengine.BooleanField(default=False)

    def __str__(self):
        return self.name

    def callback_receive_event(self, server):
        self.received_event = True
        self.save()


class FakeDevice1(event.Eventable):
    devices = mongoengine.ListField(mongoengine.ReferenceField(FakeDevice0))


def test_events_list():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    obj0 = FakeDevice0(name="hello")

    obj1 = FakeDevice1()
    obj1.devices = [obj0]

    assert 'event0' in obj0.events
    assert 'hello.event0' in obj1.events

    assert obj0.events['event0'] == obj0.event0

def test_events_list_db():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    obj0 = FakeDevice0(name="hello")
    obj0.save()

    assert 'event0' in obj0.events

    obj1 = FakeDevice0.objects(name="hello").first()
    assert isinstance(obj1, FakeDevice0)
    assert 'event0' in obj1.events

def test_callbacks_list():
    a = FakeDevice0(name="A")

    assert 'callback_receive_event' in a.callbacks
    assert 'callbacks' not in a.callbacks

    assert a.callbacks['callback_receive_event'] == a.callback_receive_event

def test_callbacks():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    a = FakeDevice0(name="A")
    a.save()

    b = FakeDevice0(name="B")
    b.save()

    assert a.received_event == False
    assert b.received_event == False

    a.event0.connect(b.callback_receive_event)

    assert a.received_event == False
    assert b.received_event == False

    a.event0(None)

    assert a.received_event == False
    assert b.received_event == False

    b.reload()
    assert b.received_event == True

def test_remove_object():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    a = FakeDevice0(name="A")
    a.save()

    b = FakeDevice0(name="B")
    b.save()

    a.event0.connect(b.callback_receive_event)

    a.delete()


if __name__ == "__main__":
    test_events_list()
    test_events_list_db()
    test_callbacks_list()
    test_callbacks()
    test_remove_object()
