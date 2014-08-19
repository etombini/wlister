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

import wlmatch
import wlactionif


class WLRule(object):

    attributes = ('uri', 'protocol', 'method', 'host', 'args')

    def __init__(self, description, log=None):

        self.matches = []

        self.action_if_match = []
        self.action_if_mismatch = []

        #oldies to be refactored
        self.prerequisite_register = []

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

        self.description = description

        # Match directive set up
        match_functions = []
        if "order" in self.description["match"]:
            match_functions = self.description["match"]["order"]
        else:
            match_functions = self.description["match"].keys()

        for m in match_functions:
            if m not in wlmatch.register:
                self.log("ERROR - " + str(m) + " is not a valid matching function for match directive")
                continue
            match_instance = wlmatch.register[m](str(self._id) + '.match.' + str(m),
                                                 self.description['match'][m],
                                                 self.log)
            self.matches.append(match_instance)

        # Action If Match directive set up
        if "action_if_match" in self.description:
            for a in self.description["action_if_match"]:
                if a not in wlactionif.register:
                    self.log("ERROR - " + str(m) + " is not a valid action function for action_if_match directive")
                    continue
                self.action_if_match.append(wlactionif.register[a](str(self._id) + "action_if_match" + str(a),
                                                                   self.description["action_if_match"][a],
                                                                   self.log))

        # Action If Mismatch directive set up
        if "action_if_mismatch" in self.description:
            for a in self.description["action_if_mismatch"]:
                if a not in wlactionif.register:
                    self.log("ERROR - " + str(m) + " is not a valid action function for action_if_mismatch directive")
                    continue
                self.action_if_mismatch.append(wlactionif.register[a](str(self._id) + "action_if_mismatch" + str(a),
                                                                      self.description["action_if_mismatch"][a],
                                                                      self.log))
        self.register_prerequisite()

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

    def analyze(self, request):
        if not self.prerequisite(request):
            return
        if self.match(request):
            for action in self.action_if_match:
                action.apply(request)
        else:
            for action in self.action_if_mismatch:
                action.apply(request)
