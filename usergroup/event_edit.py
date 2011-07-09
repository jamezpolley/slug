#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Module for creating and editing Event objects."""

# Python Imports
import logging
import os
import os.path
import simplejson
import traceback
import cStringIO as StringIO
from datetime import datetime

# Django Imports
from django import http
from django import shortcuts
from django.views.decorators import http as method
from django.contrib.auth import decorators as auth

# Third Party imports
from dateutil import rrule
from datetime_tz import datetime_tz
import markdown

# Our App imports
from usergroup import models
from usergroup import offers
from usergroup import events


# We don't want to wrap this line as we use a grep to extract the details
# pylint: disable-msg=C0301
extensions = ['abbr', 'footnotes', 'def_list', 'fenced_code', 'tables', 'subscript', 'superscript', 'slugheader', 'anyurl']


def lastfridays():
    """Return 5 last Fridays of the month."""
    return list(x.date() for x in rrule.rrule(
         rrule.MONTHLY, interval=1, count=10, byweekday=(rrule.FR(-1)),
         dtstart=datetime.now()))


def get_templates():
    """Get all the markdown templates."""
    ret = []

    directory = "templates/markdown"
    for filename in os.listdir(directory):
        if not filename.endswith('.md'):
            continue

        fullpath = os.path.join(directory, filename)
        name = filename.replace('.md', '')
        ret.append((name, file(fullpath).read()))
    return ret


@auth.login_required
@method.require_POST
def handler_offer_add(request):
    """Adds an offer to an event"""

    # /events/<key>/addoffer?id=<offerid> (POST)
    event = events.get_event_from_url(request)

    offer = shortcuts.get_object_or_404(
            models.TalkOffer, pk=request.POST.get('id', -1))

    talk = models.LightningTalk(event=event, offer=offer)
    talk.save()

    response = http.HttpResponse()
    response['Content-Type'] = 'application/javascript'
    response.write(simplejson.dumps({'key': str(talk.key())}))
    return response


@auth.login_required
@method.require_POST
def handler_offer_remove(request):
    """Removes an offer from an event."""

    # /events/<key>/removeoffer?id=<offerid> (POST)
    event = events.get_event_from_url(request)
    assert event.created_by == request.user or request.user.is_staff

    talk = shortcuts.get_object_or_404(
            models.LightningTalk, pk=request.POST.get('id', -1))
    assert talk.event == event

    talk.delete()

    response = http.HttpResponse()
    response['Content-Type'] = 'application/javascript'
    response.write(simplejson.dumps({'deleted': str(True)}))
    return response


@auth.login_required
@method.require_http_methods(["GET", "POST"])
def handler(request):
    """Handler for creating and editing Event objects."""

    assert request.user.is_staff

    # /events/<key>/edit (POST/GET)
    # /events/add (POST/GET)
    event = events.get_event_from_url(request)
    try:
        unused_events, key = request.path_info.split('/')
        if key == 'add':
            event = models.Event(created_by=request.user)
        else:
            key, unused_edit = key.split('/')
            event = shortcuts.get_object_or_404(models.Event, pk=key)
    except IndexError:
        return shortcuts.redirect('/events')

    if request.method == 'GET':
        return handler_edit_event_get(request, event)
    elif request.method == 'POST':
        return handler_edit_event_post(request, event)


@auth.login_required
@method.require_GET
def handler_edit_event_get(request, key):

    assert event.created_by == request.user or request.user.is_staff

    template_values = {}
    if event:
        template_values['agenda'] = offers.get_event_agenda(event)
    else:
        template_values['agenda'] = None

    template_values['event'] = event
    template_values['fridays'] = lastfridays()
    template_values['templates'] = get_templates()
    template_values['self'] = self
    template_values['offers'] = models.TalkOffer.objects.all()[:100]

    return shortcuts.render(
            request, 'templates/editevent.html', template_values)


@auth.login_required
@method.require_POST
def handler_edit_event_post(request, event):

    assert event.created_by == request.user or request.user.is_staff

    start_date = datetime_tz.smartparse(request.REQUEST['start'])
    end_date = datetime_tz.smartparse(request.REQUEST['end'])

    event.input = request.REQUEST['input']
    event.start = start_date.asdatetime()
    event.end = end_date.asdatetime()

    event.save()

    # We can't do this template subsitution until we have saved the event.
    try:
        plaintext = str(template.Template(inputtext).render(
                        template.Context({
                            'event': event,
                            'req': request,
                            'agenda': offers.get_event_agenda(event)
                        }), ))
        html = markdown.markdown(plaintext, extensions).encode('utf-8')
        event.plaintext = plaintext
        event.html = html
    except Exception:
        sio = StringIO.StringIO()
        traceback.print_exc(file=sio)
        event.plaintext = sio.getvalue()

    logging.debug("e.a %s, e.n %s", event.announcement, event.name)

    event.save()

    return django.shortcuts.redirect('%s/edit' % event.get_url())
