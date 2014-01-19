#!/usr/bin/env python
# -*- coding: utf-8 -*-

import event
import mongoengine


class FakeDevice0(event.Object):
    event0 = mongoengine.ReferenceField(event.Event, required=True)
    name = mongoengine.StringField()

    def __str__(self):
        return self.name

    @staticmethod
    def create(name):
        o = FakeDevice0(name=name)
        o.event0 = event.Event()
        return o


class FakeDevice1(event.Object):
    devices = mongoengine.ListField(mongoengine.ReferenceField(FakeDevice0))


def test_events_list():
    obj0 = FakeDevice0.create(name="hello")

    obj1 = FakeDevice1()
    obj1.devices = [obj0]

    assert 'event0' in obj0.events
    assert 'hello.event0' in obj1.events

    assert obj0.events['event0'] == obj0.event0

def test_callbacks():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')


if __name__ == "__main__":
    test_events_list()
