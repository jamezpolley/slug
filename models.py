#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Module contains the models of objects used in the application."""

import config
config.setup()

from google.appengine.ext import db

# Some clever namespaces to make it easier to understand.
# pylint: disable-msg=W0404
from google.appengine.ext import db as appengine
from aeoid import users as openid


class Announcement(db.Model):
    """An announcement for an event."""
    created_by = openid.UserProperty(
            auto_current_user_add=True, required=True)
    created_on = db.DateTimeProperty(
            auto_now_add=True, required=True)

    name = db.StringProperty(required=True)
    plaintext = db.TextProperty()
    html = db.BlobProperty()

    published_by = appengine.UserProperty(
            auto_current_user_add=True, required=True)
    published_on = db.DateTimeProperty(
            auto_now_add=True, required=True)


class Event(db.Model):
    """An event."""

    def get_url(self):
        """Return the canonical url for an event."""
        return "/event/%s" % self.key().id()

    created_by = appengine.UserProperty(
            auto_current_user_add=True, required=True)
    created_on = db.DateTimeProperty(
            auto_now_add=True, required=True)

    name = db.StringProperty(required=True)
    input = db.TextProperty()
    plaintext = db.TextProperty()
    html = db.BlobProperty()

    published = db.BooleanProperty(default=False)
    announcement = db.ReferenceProperty(Announcement)

    emailed = db.BooleanProperty(default=False)

    start = db.DateTimeProperty(required=True)
    end = db.DateTimeProperty(required=True)


class TalkOffer(db.Model):
    """An lightning talk to be given at an event."""
    created_by = openid.UserProperty(
            auto_current_user_add=True, required=True)
    created_on = db.DateTimeProperty(
            auto_now_add=True, required=True)

    name = db.StringProperty(required=True)
    text = db.TextProperty()
    seconds = db.IntegerProperty()
    consent = db.BooleanProperty()

class LigtningTalk(db.Model):
    created_by = openid.UserProperty(
            auto_current_user_add=True, required=True)
    created_on = db.DateTimeProperty(
            auto_now_add=True, required=True)

    offer = db.ReferenceProperty(TalkOffer, required=True,
            collection_name='events')
    event = db.ReferenceProperty(Event, required=True,
            collection_name='talks')

class Response(db.Model):
    """An RSVP to attend an event."""
    created_by = openid.UserProperty(
            auto_current_user_add=True, required=True)
    created_on = db.DateTimeProperty(
            auto_now_add=True, required=True)

    event = db.ReferenceProperty(Event, collection_name="responses")

    attending = db.BooleanProperty(required=True, default=True)

    # Should the response be hidden from everyone?
    #hide = db.BoolenProperty(required=False, default=False)

    # If this is a guest, then we store their details here, otherwise we just
    # use the creater's details.
    guest = db.BooleanProperty(required=True, default=False)
    guest_name = db.StringProperty()
    guest_email = db.EmailProperty()
