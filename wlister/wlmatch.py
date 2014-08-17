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
import jsonschema


register = {}


class WLMatcher(object):

    def __init__(self, name=None, log=None):
        self.name = name
        if log is None:
            def log_nothing(message):
                pass
            self.log = log_nothing
        else:
            self.log = log

    def match(self, request):
        raise NotImplementedError


class WLMatchAttribute(WLMatcher):

    attributes = ('uri', 'protocol', 'method', 'host', 'args')

    def __init__(self, name=None, attribute=None, regex=None, log=None):
        WLMatcher.__init__(self, name, log)
        if attribute not in self.attributes:
            raise ValueError
        else:
            self.attribute = attribute
        self.regex = re.compile(regex)

    def match(self, request):
        try:
            return self.regex.match(getattr(request, self.attribute))
        except:
            return False


class WLMatchURI(WLMatchAttribute):

    def __init__(self, name=None, regex=None, log=None):
        WLMatchAttribute.__init__(self, name, "uri", regex, log)

register["uri"] = WLMatchURI


class WLMatchProtocol(WLMatchAttribute):

    def __init__(self, name=None, regex=None, log=None):
        WLMatchAttribute.__init__(self, name, 'protocol', regex, log)

register["protocol"] = WLMatchProtocol


class WLMatchMethod(WLMatchAttribute):

    def __init__(self, name=None, regex=None, log=None):
        WLMatchAttribute.__init__(self, name, "method", regex, log)

register["method"] = WLMatchMethod


class WLMatchHost(WLMatchAttribute):

    def __init__(self, name=None, regex=None, log=None):
        WLMatchAttribute.__init__(self, name, "host", regex, log)

register["host"] = WLMatchHost


class WLMatchArgs(WLMatchAttribute):

    def __init__(self, name=None, regex=None, log=None):
        WLMatchAttribute.__init__(self, name, "args", regex, log)

register["args"] = WLMatchArgs

class WLMatchItems(WLMatcher):

    items = ["parameters", "headers", "content_url_encoded"]

    def __init__(self, name=None, item=None, regex=None, log=None):
        WLMatcher.__init__(self, name=name, log=log)
        if item not in self.items:
            self.log('ERROR - ' + str(item) + " is not a valid keyword (parameters, headers, content_url_encoded)")
            raise ValueException
        self.item = item
        self.re_items = []
        self.re_len = 0
        sorted_regex = sorted(regex, key=lambda p: p[0])
        for name, value in sorted_regex:
            try:
                self.re_items.append((name, re.compile(value)))
            except Exception as e:
                self.log("Can not compile regex '" + str(value) + "' - " + str(e))
        self.re_len = len(self.re_items)

    def match(self, request):
        if getattr(request, self.item) is None:
            return False
        item = getattr(request, self.item)
        if len(item) != self.re_len:
            return False
        i = 0
        while i < self.re_len:
            if item[i][0] != self.re_items[i][0]:
                return False
            if not self.re_items[i][1].match(item[i][1]):
                return False
            i = i + 1
        return True


class WLMatchParameters(WLMatchItems):
    """
        There may be a bug when there are duplicated parameters
    """
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItems.__init__(self, name, "parameters", regex, log)

register["parameters"] = WLMatchParameters

class WLMatchHeaders(WLMatchItems):
    """
    """
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItems.__init__(self, name, "headers", regex, log)

register["headers"] = WLMatchHeaders

class WLMatchContentURLEncoded(WLMatchItems):
    """
    """
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItems.__init__(self, name, "content_url_encoded", regex, log)

register["content_url_encoded"] = WLMatchContentURLEncoded

class WLMatchContentJSON(WLMatcher):

    def __init__(self, name=None, regex=None, log=None):
        WLMatcher.__init__(self, name, log)
        self.re_content_json = regex

    def match(self, request):
        if request.content_json is None:
            return False
        try:
            jsonschema.validate(request.content_json, self.re_content_json)
        except:
            return False
        return True

register["content_json"] = WLMatchContentJSON

class WLMatchItemsIn(WLMatcher):

    items = ["parameters", "headers", "content_url_encoded"]

    def __init__(self, name=None, item=None, regex=None, log=None):
        WLMatcher.__init__(self, name=name, log=log)
        if item not in self.items:
            self.log("Error - " + str(item) + " is not a valid keyword (parameters, headers, content_url_encoded)")
            raise ValueException
        self.item = item
        self.re_items = []
        self.re_len = 0
        sorted_regex = sorted(regex, key=lambda p: p[0])
        for name, value in sorted_regex:
            try:
                self.re_items.append((name, re.compile(value)))
            except Exception as e:
                self.log("Can not compile regex '" + str(value) + "' - " + str(e))
        self.re_len = len(self.re_items)

    def match(self, request):
        if getattr(request, self.item) is None:
            return False
        item = getattr(request, self.item)
        idx_re = 0
        for name, value in item:
            #if self.re_items < name:
            #    return False
            if name == self.re_items[idx_re][0] \
                    and self.re_items[idx_re][1].match(value):
                idx_re = idx_re + 1
            if idx_re == self.re_len:
                return True
        return False

class WLMatchParametersIn(WLMatchItemsIn):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsIn.__init__(self, name, "parameters", regex, log)

register["parameters_in"] = WLMatchParametersIn

class WLMatchHeadersIn(WLMatchItemsIn):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsIn.__init__(self, name, "headers", regex, log)

register["headers_in"] = WLMatchHeadersIn

class WLMatchContentURLEncodedIn(WLMatchItemsIn):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsIn.__init__(self, name, "content_url_encoded", regex, log)

register["content_url_encoded_in"] = WLMatchContentURLEncodedIn

class WLMatchItemsList(WLMatcher):

    items = ["parameters", "headers", "content_url_encoded"]

    def __init__(self, name=None, item=None, regex=None, log=None):
        WLMatcher.__init__(self, name=name, log=log)
        if item not in self.items:
            self.log("Error - " + str(item) + " is not a valid keyword (parameters_list, headers_list, content_url_encodedi_list)")
            raise ValueException
        self.item = item
        self.re_item = regex # which is a list of "items" ("parameters", "headers", "content_url_encoded")

    def match(self, request):
        if getattr(request, self.item) is None:
            return False
        request_items = [name for name, value in getattr(request, self.item)]
        # lists are sorted
        return request_items == self.re_item

class WLMatchParametersList(WLMatchItemsList):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsList.__init__(self, name, "parameters", regex, log)

register["parameters_list"] = WLMatchParametersList

class WLMatchHeadersList(WLMatchItemsList):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsList.__init__(self, name, "headers", regex, log)

register["headers_list"] = WLMatchParametersList

class WLMatchContentURLEncodedList(WLMatchItemsList):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsList.__init__(self, name, "content_url_encoded", regex, log)

register["content_url_encoded_list"] = WLMatchContentURLEncodedList

class WLMatchItemsListIn(WLMatcher):

    items = ["parameters", "headers", "content_url_encoded"]

    def __init__(self, name=None, item=None, regex=None, log=None):
        WLMatcher.__init__(self, name=name, log=log)
        if item not in self.items:
            self.log("Error - " + str(item) + " is not a valid keyword (parameters_list_in, headers_list_in, content_url_encoded_list_in)")
            raise ValueException
        self.item = item
        self.re_items = sorted(regex)
        self.re_len = len(self.re_items)

    def match(self, request):
        if getattr(request, self.item) is None:
            return False
        item = getattr(request, self.item)
        idx_re = 0
        for name, value in item:
            if name == self.re_items[idx_re]:
                idx_re = idx_re + 1
            if idx_re == self.re_len:
                return True
        return False

class WLMatchParametersListIn(WLMatchItemsListIn):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsListIn.__init__(self, name, "parameters", regex, log)

register["parameters_list_in"] = WLMatchParametersListIn

class WLMatchHeadersListIn(WLMatchItemsListIn):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsListIn.__init__(self, name, "headers", regex, log)

register["headers_list_in"] = WLMatchHeadersListIn

class WLMatchContentURLEncodedListIn(WLMatchItemsListIn):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsListIn.__init__(self, name, "content_url_encoded", regex, log)

register["content_url_encoded_list_in"] = WLMatchContentURLEncodedListIn

class WLMatchItemsAllUnique(WLMatcher):

    items = ["parameters", "headers", "content_url_encoded"]

    def __init__(self, name=None, item=None, regex=None, log=None):
        WLMatcher.__init__(self, name=name, log=log)
        if item not in self.items:
            self.log("ERROR - " + str(self.name) + " - " + str(item) + " is not a valid keyword (parameters_list_in, headers_list_in, content_url_encoded_list_in)")
            raise ValueException
        if regex == "True":
            self.re_items = True
        elif regex == "False":
            self.re_items = False
        else:
            self.log("ERROR - " + str(self.name) + " - " + str(regex) + " is not a valid value (must be \"True\" or \"False\", with quotes)")
            raise ValueException
        self.item = item

    def match(self, request):
        if getattr(request, self.item) is None:
            return False
        l = [name for name, value in getattr(request, self.item)]
        return self.re_items == (len(l) == len(set(l)))

class WLMatchParametersAllUnique(WLMatchItemsAllUnique):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsAllUnique.__init__(self, name, "parameters", regex, log)

register["parameters_all_unique"] = WLMatchParametersAllUnique

class WLMatchHeadersAllUnique(WLMatchItemsAllUnique):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsAllUnique.__init__(self, name, "headers", regex, log)

register["headers_all_unique"] = WLMatchHeadersAllUnique

class WLMatchContentURLEncodedAllUnique(WLMatchItemsAllUnique):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsAllUnique.__init__(self, name, "content_url_encoded", regex, log)

register["content_url_encoded_all_unique"] = WLMatchContentURLEncodedAllUnique

class WLMatchItemsUnique(WLMatcher):

    items = ["parameters", "headers", "content_url_encoded"]

    def __init__(self, name=None, item=None, regex=None, log=None):
        WLMatcher.__init__(self, name=name, log=log)
        if item not in self.items:
            self.log("ERROR - " + str(self.name) + " - " + str(item) + " is not a valid keyword (parameters_list_in, headers_list_in, content_url_encoded_list_in)")
            raise ValueError
        self.item = item
        self.re_items = regex

    def match(self, request):
        if getattr(request, self.item) is None:
            return False
        l_name = [name for name, value in getattr(request, self.item)]
        for name in self.re_items:
            if l_name.count(name) != 1:
                return False
        return True

class WLMatchParametersUnique(WLMatchItemsUnique):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsUnique.__init__(self, name, "parameters", regex, log)

register["parameters_unique"] = WLMatchParametersUnique

class WLMatchHeadersUnique(WLMatchItemsUnique):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsUnique.__init__(self, name, "headers", regex, log)

register["headers_unique"] = WLMatchHeadersUnique

class WLMatchContentURLEncodedUnique(WLMatchItemsUnique):
    def __init__(self, name=None, regex=None, log=None):
        WLMatchItemsUnique.__init__(self, name, "content_url_encoded", regex, log)

register["content_url_encoded_unique"] = WLMatchContentURLEncodedUnique


