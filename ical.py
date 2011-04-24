#!/usr/bin/python

"""Generate iCal feed based on events in database."""

import config
import pprint
import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import models
import datetime
import icalendar

class iCal(webapp.RequestHandler):

    def addEventToCal(self, event, cal):
        """Takes a models.Event, addes it to the calendar/

        Arguments:
        	event: a models.Event
            cal: an icalendar.Calendar
        """

        cal_event = icalendar.Event()
        cal_event.add('summary', event.name)
        cal_event.add('dt_start', event.start)
        cal_event.add('dt_end', event.end)
        cal_event.add('dtstamp', event.created_on)
        cal_event['uid'] = event.key
        cal_event.add('priority', 5)

        cal.add_component(cal_event)


    def get(self):
        cal = icalendar.Calendar()
        cal.add('prodid', 'SLUG Event System//signup.slug.org.au//')
        cal.add('version', '2.0')

        events = models.Event.all()

        for event in events:
            self.addEventToCal(event, cal)

        self.response.out.write(cal.as_string())

