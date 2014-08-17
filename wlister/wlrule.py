# -*- coding: utf-8 -*-

# Copyright (c) 2014, Elvis Tombini <elvis@mapom.me>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from collections import OrderedDict
import re
import jsonschema
import wlmatch


class WLRule(object):

    attributes = ('uri', 'protocol', 'method', 'host', 'args')

    def __init__(self, description, log=None):

        self.matches = []

        self.prerequisite_register = []
        self.action_if_match_register = []
        self.action_if_mismatch_register = []

        if 'id' in description:
            self._id = description['id']
        else:
            self._id = str(id(self))

        # method used to log messages
        if log is None:
            def log_nothing(message):
                pass
            self.log = log_nothing
        else:
            self.log = log

        if type(description) is not dict:
            raise TypeError("Description parameter must be a dictionary")
        self.description = description

        match_functions = []
        if "order" in self.description["match"]:
            match_functions = self.description["match"]["order"]
        else:
            match_functions = self.description["match"].keys()

        for m in match_functions:
            if m not in wlmatch.register:
                self.log("ERROR - " + str(m) + " is not a valid matching function")
                continue
            match_instance = wlmatch.register[m](str(self._id) + '.match.' + m,
                                                 self.description['match'][m],
                                                 self.log)
            self.matches.append(match_instance)

        self.register_prerequisite()
        self.init_action_if_match()
        self.init_action_if_mismatch()

    def register_prerequisite(self):
        # prerequisites material and prerequisites_* function registration
        if 'prerequisite' not in self.description:
            return
        self.has_tag = None
        self.has_not_tag = None
        if 'has_tag' in self.description['prerequisite']:
            if type(self.description['prerequisite']['has_tag']) is list:
                self.has_tag = self.description['prerequisite']['has_tag']
            else:
                self.has_tag = [self.description['prerequisite']['has_tag']]
            self.prerequisite_register.append('prerequisite_has_tag')

        if 'has_not_tag' in self.description['prerequisite']:
            if type(self.description['prerequisite']['has_not_tag']) is list:
                self.has_not_tag = \
                    self.description['prerequisite']['has_not_tag']
            else:
                self.has_not_tag = \
                    [self.description['prerequisite']['has_not_tag']]
            self.prerequisite_register.append('prerequisite_has_not_tag')

    def init_action_if_match(self):
        # list of methodes that must be used if matching is validated
        self.action_if_match_register = []
        # if_match material and if_match_* function registration
        try:
            self.if_match_set_tag = \
                self.description['action_if_match']['set_tag']
            if type(self.if_match_set_tag) is not list:
                self.if_match_set_tag = [self.if_match_set_tag]
            self.action_if_match_register.append('action_if_match_set_tag')
        except:
            self.if_match_set_tag = None

        try:
            self.if_match_unset_tag = \
                self.description['action_if_match']['unset_tag']
            if type(self.if_match_unset_tag) is not list:
                self.if_match_unset_tag = [self.if_match_unset_tag]
            self.action_if_match_register.append['action_if_match_unset_tag']
        except:
            self.if_match_unset_tag = None

        try:
            self.if_match_whitelist = \
                self.description['action_if_match']['whitelist']
            self.action_if_match_register.append('action_if_match_whitelist')
        except:
            self.if_match_whitelist = None

        try:
            self.if_match_blacklist = \
                self.description['action_if_match']['blacklist']
            self.action_if_match_register.append('action_if_match_blacklist')
        except:
            self.if_match_blacklist = None

    def init_action_if_mismatch(self):
        # list of methods that must be used if matching is not validated
        self.action_if_mismatch_register = []
        # if_mismatch material and if_mismatch_* function registration
        try:
            self.if_mismatch_set_tag = \
                self.description['action_if_mismatch']['set_tag']
            if type(self.if_mismatch_set_tag) is not list:
                self.if_mismatch_set_tag = [self.if_mismatch_set_tag]
            self.action_if_mismatch_register.append('action_if_mismatch_set_tag')
        except:
            self.if_mismatch_set_tag = None

        try:
            self.if_mismatch_unset_tag = \
                self.description['action_if_mismatch']['unset_tag']
            if type(self.if_mismatch_unset_tag) is not list:
                self.if_mismatch_unset_tag = [self.if_mismatch_unset_tag]
            self.action_if_mismatch_register.append('action_if_mismatch_unset_tag')
        except:
            self.if_mismatch_unset_tag = None

        try:
            self.if_mismatch_whitelist = \
                self.description['action_if_mismatch']['whitelist']
            self.action_if_mismatch_register.append('action_if_mismatch_whitelist')
        except:
            self.if_mismatch_whitelist = None

        try:
            self.if_mismatch_blacklist = \
                self.description['action_if_mismatch']['blacklist']
            self.action_if_mismatch_register.append('action_if_mismatch_blacklist')
        except:
            self.if_mismatch_blacklist = None

    # main match function
    # other match_* functions are not meant to be called
    def match(self, request):
        for m in self.matches:
            if not m.match(request):
                return False
        return True

    def prerequisite_has_tag(self, request):
        if self.has_tag is None:
            return True
        has_tag = True
        for tag in self.has_tag:
            if tag not in request.tags:
                has_tag = False
                break
        return has_tag

    def prerequisite_has_not_tag(self, request):
        if self.has_not_tag is None:
            return True
        has_not_tag = True
        for tag in self.has_not_tag:
            if tag in request.tags:
                has_not_tag = False
                break
        return has_not_tag

    # main prerequisite validator
    def prerequisite(self, request):
        for f in self.prerequisite_register:
            if not getattr(self, f)(request):
                return False
        return True

    def action_if_match_set_tag(self, request):
        if self.if_match_set_tag is None:
            return
        for t in self.if_match_set_tag:
            request.tags.add(t)

    def action_if_match_unset_tag(self, request):
        if self.if_match_unset_tag is None:
            return
        for t in self.if_match_unset_tag:
            request.tags.discard(t)

    def action_if_match_whitelist(self, request):
        if self.if_match_whitelist is None:
            request.whitelisted = False
            return
        if self.if_match_whitelist == 'True':
            request.whitelisted = True
            return
        if self.if_match_whitelist == 'False':
            request.whitelisted = False
            return

    def action_if_match_blacklist(self, request):
        if self.if_match_blacklist is None:
            request.blacklisted = False
            return
        if self.if_match_blacklist == 'True':
            request.blacklisted = True
            return
        if self.if_match_blacklist == 'False':
            request.blacklisted = False
            return

    # main action_if_match hook
    def action_if_match(self, request):
        for action in self.action_if_match_register:
            getattr(self, action)(request)

    def action_if_mismatch_set_tag(self, request):
        if self.if_mismatch_set_tag is None:
            return
        for t in self.if_mismatch_set_tag:
            request.tags.add(t)

    def action_if_mismatch_unset_tag(self, request):
        if self.if_mismatch_unset_tag is None:
            return
        for t in self.if_mismatch_unset_tag:
            request.tags.discard(t)

    def action_if_mismatch_whitelist(self, request):
        if self.if_mismatch_whitelist is None:
            request.whitelisted = False
            return
        if self.if_mismatch_whitelist == 'True':
            request.whitelisted = True
            return
        if self.if_mismatch_whitelist == 'False':
            request.whitelisted = False
            return

    def action_if_mismatch_blacklist(self, request):
        if self.if_mismatch_blacklist is None:
            request.blacklisted = False
            return
        if self.if_mismatch_blacklist == 'True':
            request.blacklisted = True
            return
        if self.if_mismatch_blacklist == 'False':
            request.blacklisted = False
            return

    # main action_if_mismatch hook
    def action_if_mismatch(self, request):
        for action in self.action_if_mismatch_register:
            getattr(self, action)(request)

    def analyze(self, request):
        if not self.prerequisite(request):
            return
        if self.match(request):
            self.action_if_match(request)
        else:
            self.action_if_mismatch(request)
