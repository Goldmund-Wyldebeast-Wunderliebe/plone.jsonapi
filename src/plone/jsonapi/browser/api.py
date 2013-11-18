# -*- coding: utf-8 -*-
#
# File: api.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging
from plone import api

from zope import component

from zope.interface import implements

from Products.Five import BrowserView
from zope.publisher.interfaces import IPublishTraverse

from decorators import runtime
from decorators import returns_json
from decorators import handle_errors

from interfaces import IAPI
from interfaces import IRouter

from plone.jsonapi.browser.helpers import apply_ska_authentication

logger = logging.getLogger("plone.jsonapi")


class API(BrowserView):
    """ JSON API Framework
    """
    implements(IAPI, IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.traverse_subpath = []
        apply_ska_authentication(context, request)

    def publishTraverse(self, request, name):
        """ get's called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    @handle_errors
    def dispatch(self):
        """ dispatches the given subpath to the router
        """
        current_user = api.user.get_current()
        logger.info("current_user: {0}".format(current_user))

        path = "/".join(self.traverse_subpath)
        for name, router in component.getUtilitiesFor(IRouter):
            router.initialize(self.context, self.request)
            if router.match(self.context, self.request, path):
                return router(self.context, self.request, path)

    @returns_json
    @runtime
    def __call__(self):
        """ render json on __call__
        """
        return self.dispatch()

# vim: set ft=python ts=4 sw=4 expandtab :
