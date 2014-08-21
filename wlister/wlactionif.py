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

import re

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


class WLLog(WLActionIf):
    re_header = re.compile("headers\[(?P<header_name>[^]]*)\]")
    re_parameter = re.compile("parameters\[(?P<parameter_name>[^]]*)\]")
    re_content_url_encoded = re.compile("content_url_encoded\[(?P<content_url_encoded_name>[^]]*)\]")

    def __init__(self, name=None, parameters=None, log=None):
        WLActionIf.__init__(self, name, log)
        #self.log("DEBUG - logging > " + str(parameters))
        if type(parameters) is not list:
            self.log("ERROR - " + self.name +
                     " - log parameter must be a list of list of string")
            raise ValueError("log parameter must be a list of list of string")
        for p in parameters:
            if type(p) is not list:
                self.log("ERROR - " + self.name +
                         " - log parameter must be a list of list of string")
                raise ValueError("log parameter must be a list of list of string")
        self.parameters = parameters

    def apply(self, request):
        for log_directive in self.parameters:
            log_line = [str(request.request_id)]
            for p in log_directive:
                if p[0] == "#":
                    log_line.append(p[1:])
                    continue
                try:
                    log_line.append(str(getattr(request, p)))
                except AttributeError:
                    m = self.re_header.match(p)
                    if m:
                        try:
                            header_name = m.group("header_name")
                            log_line.append(str([(name, value) for name, value in request.headers if name == header_name]))
                        except Exception as e:
                            self.log("ERROR - " + self.name +
                                    " - can not find request header " + str(p) + " - " + str(e))
                            log_line.append(p)
                        continue
                    m = self.re_parameter.match(p)
                    if m:
                        try:
                            parameter_name = m.group("parameter_name")
                            log_line.append(str([(name, value) for name, value in request.parameters if name == parameter_name]))
                        except:
                            self.log("ERROR - " + self.name +
                                    " - can not find request parameter " + str(p))
                            log_line.append(p)
                        continue
                    m = self.re_content_url_encoded.match(p)
                    if m:
                        try:
                            content_url_encoded_name = m.group("content_url_encoded_name")
                            log_line.append(str([(name, value) for name, value in request.content_url_encoded if name == content_url_encoded_name]))
                        except Exception as e:
                            self.log("ERROR - " + self.name +
                                    " - can not find content_url_encoded parameter " + str(p) + " - " + str(e))
                        continue
            if len(log_line) > 1:
                self.log(' '.join(log_line))

register["log"] = WLLog
