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

class WLPrerequisite(object):
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


class WLHasTag(WLPrerequisite):
    def __init__(self, name=None, parameters=None, log=None):
        WLPrerequisite.__init__(self, name, log)
        if parameters is None or \
                type(parameters) is not list:
            self.log("ERROR - " + self.name +
                     " - has_tag parameter must be a list of strings as in [\"tag01\", \"tag02\"], \"" +
                     str(parameters) + "\" provided")
            raise ValueError

    def apply(self, request):
        for tag in self.parameters:
            if tag not in request.tags:
                return False
        return True

register["has_tag"] = WLHasTag

class WLHasNotTag(WLPrerequisite):
    def __init__(self, name=None, parameters=None, log=None):
        WLPrerequisite.__init__(self, name, log)
        if parameters is None or \
                type(parameters) is not list:
            self.log("ERROR - " + self.name +
                     " - has_not_tag parameter must be a list of strings as in [\"tag01\", \"tag02\"], \"" +
                     str(parameters) + "\" provided")
            raise ValueError

    def apply(self, request):
        for tag in self.parameters:
            if tag in request.tags:
                return False
        return True

register["has_not_tag"] = WLHasNotTag


#class WLBlacklist(WLPrerequisite):
#    def __init__(self, name=None, parameters=None, log=None):
#        WLPrerequisite.__init__(self, name, log)
#        if parameters == "True":
#            self.parameters = True
#        elif parameters == "False":
#            self.parameters = False
#        else:
#            self.log("ERROR - " + self.name
#                     + " - blacklist parameter must be \"True\" or \"False\", \""
#                     + str(parameters) + " \" provided")
#            raise ValueError
#
#    def apply(self, request):
#        request.blacklisted = self.parameters
#
#register["blacklist"] = WLBlacklist
#
#class WLSetTag(WLPrerequisite):
#    def __init__(self, name=None, parameters=None, log=None):
#        WLPrerequisite.__init__(self, name, log)
#        if type(parameters) is not list:
#            self.log("ERROR - " + self.name
#                     + " - set_tag parameter must be a list of string as in [\"tag01\", \"tag02\"]")
#            raise ValueError
#        self.parameters = parameters
#
#    def apply(self, request):
#        for t in self.parameters:
#            request.tags.add(t)
#
#register["set_tag"] = WLSetTag
#
#class WLUnsetTag(WLPrerequisite):
#    def __init__(self, name=None, parameters=None, log=None):
#        WLPrerequisite.__init__(self, name, log)
#        if type(parameters) is not list:
#            self.log("ERROR - " + self.name
#                     + " - unset_tag parameter must be a list of string as in [\"tag01\", \"tag02\"]")
#            raise ValueError
#        self.parameters = parameters
#
#    def apply(self, request):
#        for t in self.parameters:
#            request.tags.discard(t)
#
#register["unset_tag"] = WLUnsetTag



