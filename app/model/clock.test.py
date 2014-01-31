#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clock
import mongoengine


def test_clock_event_mask():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    event = clock.Event(name="hello")

    assert event.week_days_mask == 0

    event.set_week_day_mask(0, True)
    assert event.week_days_mask == 0x01
    assert event.week_day_mask(0)
    assert not event.week_day_mask(3)

    event.set_week_day_mask(3, True)
    assert event.week_days_mask == 0x09
    assert event.week_day_mask(0)
    assert event.week_day_mask(3)

    event.set_week_day_mask(0, False)
    assert event.week_days_mask == 0x08
    assert not event.week_day_mask(0)
    assert event.week_day_mask(3)


if __name__ == "__main__":
    test_clock_event_mask()
