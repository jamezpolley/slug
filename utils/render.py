#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import config
config.setup()

from google.appengine.api import users as appengine_users
from google.appengine.ext.webapp import template
import aeoid.users as openid_users

import gravatar

def render(t, kw):
  req = kw['self'].request
  extra = {
      'req': req,
      'config': config,
      'openid_user': openid_users.get_current_user(),
      'openid_login_jsurl': openid_users.create_login_url('/refresh'),
      'openid_login_url': openid_users.create_login_url(req.path),
      'openid_logout_url': openid_users.create_logout_url(req.path),
      'appengine_user': appengine_users.get_current_user(),
      'appengine_admin': appengine_users.is_current_user_admin(),
      'appengine_logout_url': appengine_users.create_logout_url(req.path),
      }

  # Don't let people trample on these variables
  common = set(extra.keys()).intersection(kw.keys())
  if common:
    raise SystemError('The following keys are reserved %s' % common)

  kw.update(extra)
  return template.render(t, kw)
