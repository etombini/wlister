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

register = {}


class WLActionIf(object):
    def __init__(self, name=None, log=None):
        self.name = str(name)
        if log is None:
            def log_nothing(message):
                pass
            self.log = log_nothing
        else:
            self.log = log

    def apply(self, request):
        raise NotImplementedError


class WLWhitelist(WLActionIf):
    def __init__(self, name=None, parameters=None, log=None):
        WLActionIf.__init__(self, name, log)
        if parameters == "True":
            self.parameters = True
        elif parameters == "False":
            self.parameters = False
        else:
            self.log("ERROR - " + self.name
                     + " - whitelist parameter must be \"True\" or \"False\", \""
                     + str(parameters) + " \" provided")
            raise ValueError

    def apply(self, request):
        request.whitelisted = self.parameters

register["whitelist"] = WLWhitelist


class WLBlacklist(WLActionIf):
    def __init__(self, name=None, parameters=None, log=None):
        WLActionIf.__init__(self, name, log)
        if parameters == "True":
            self.parameters = True
        elif parameters == "False":
            self.parameters = False
        else:
            self.log("ERROR - " + self.name
                     + " - blacklist parameter must be \"True\" or \"False\", \""
                     + str(parameters) + " \" provided")
            raise ValueError

    def apply(self, request):
        request.blacklisted = self.parameters

register["blacklist"] = WLBlacklist


class WLSetTag(WLActionIf):
    def __init__(self, name=None, parameters=None, log=None):
        WLActionIf.__init__(self, name, log)
        if type(parameters) is not list:
            self.log("ERROR - " + self.name
                     + " - set_tag parameter must be a list of string as in [\"tag01\", \"tag02\"]")
            raise ValueError
        self.parameters = parameters

    def apply(self, request):
        for t in self.parameters:
            request.tags.add(t)

register["set_tag"] = WLSetTag


class WLUnsetTag(WLActionIf):
    def __init__(self, name=None, parameters=None, log=None):
        WLActionIf.__init__(self, name, log)
        if type(parameters) is not list:
            self.log("ERROR - " + self.name
                     + " - unset_tag parameter must be a list of string as in [\"tag01\", \"tag02\"]")
            raise ValueError
        self.parameters = parameters

    def apply(self, request):
        for t in self.parameters:
            request.tags.discard(t)

register["unset_tag"] = WLUnsetTag


class WLSetHeader(WLActionIf):
    def __init__(self, name=None, parameters=None, log=None):
        WLActionIf.__init__(self, name, log)
        if type(parameters) is not list:
            self.log("ERROR - " + self.name +
                     " - set_header parameter must be a list of string as in [\"x-specific-header\", \"header_value\"]")
            raise ValueError
        self.parameters = parameters

    def apply(self, request):
        try:
            request.request.headers_in.add(self.parameters[0], self.parameters[1])
            request.headers.append(self.parameters)
        except Exception as e:
            self.log("ERROR - " + self.name + " - Something wrong happened when adding new header \"" +
                     str(self.parameters) + "\" > " + str(e))

register["set_header"] = WLSetHeader
