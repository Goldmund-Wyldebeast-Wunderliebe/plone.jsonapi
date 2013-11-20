# -*- coding: utf-8 -*-
#
# File: helpers.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging

from zope.globalrequest import getRequest
from plone import api

from resato.dms.api.helpers import is_authentic

logger = logging.getLogger("plone.jsonapi")

def error(message, **kw):
    result = {"success": False, "error": message}
    if kw:
        result.update(kw)
    return result

def success(message, **kw):
    result = {"success": True,
            "message": message}
    if kw:
        result.update(kw)

    return result

def get_member(request):
    """
    Get username from request (GET param `auth_user`) and return member object.

    :FIXME: Move this elsewhere if you know a better place.
    """
    portal = api.portal.get()

    auth_user = request.get('auth_user')

    username = portal.portal_dms[auth_user]

    if username:
        member = api.user.get(username)
        return member

def apply_ska_authentication(context, request=None):
    """
    Applies `ska` authentication where necessary. Checks if `valid_until`, `auth_user` and `signature` GET
    variables are present in the URL and applies the authentication then.

    :FIXME: Move this elsewhere if you know a better place.
    """
    if not request:
        request = getRequest()

    if request.get('valid_until') and request.get('auth_user') and request.get('signature'):
        logger.info("Applying `ska` authentication")
        if not request.get('authenticated'):
            member = None
            try:
                member = is_authentic()
            except Exception as e:
                logger.info("Member `ska` credentials not accepted")

            if member:
                logger.info("Redirecting...")
                user_id = member.getId()
                context.acl_users.session._setupSession(user_id, context.REQUEST.RESPONSE)
                new_url = "{0}?{1}&authenticated=true".format(
                    request.get('ACTUAL_URL'),
                    request.get('QUERY_STRING')
                    )
                request.response.redirect(new_url)
                logger.info("Redirect!")
        else:
            logger.info("Not redirected")

        logger.info("When redirecting, you shouldn't see this!")
    else:
        logger.info("NOT applying `ska` authentication!")

# vim: set ft=python ts=4 sw=4 expandtab :
