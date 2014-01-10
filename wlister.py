# -*- coding: utf-8

from mod_python import apache

import uuid
import re

rules = [
    {
        "id": "000000",
        "match":
        {
            "url": "^/\d+/\d+$",
            "protocol": "^HTTP/1\.1$",
            "method": "^GET$",
            "host": "^mapom.me$",
            "raw_parameters" : "^$",
            "ip": "^127\.0\.0\.1$",
            "headers":
            {
                "Content-Type": "^application/x-www-form-urlencoded$",
                "Host": "^mapom.me$"
            }
        },
        "prerequisites":
        {
            "has_tag": ["tag01", "tag02"]
        },
        "actions_if_match":
        {
            "set_tag": ["tag03", "tag04"],
            "unset_tag": ["tag01"],
            "set_whitelisted": True
        },
        "actions_if_mismatch":
        {
            "set_tag": ["blah", "blih"]
        }
    }
]


class WLRule(object):
    def __init__(self, description):
        if type(description) is not dict:
            raise TypeError("Description parameter must be a dictionary")
        self.description = description
        # From description, building utility objects and/or functions

        try:
            self.re_url = re.compile(self.description['match']['url'])
        except:
            self.re_url = None

        try:
            self.re_protocol = re.compile(self.description['match']['protocol'])
        except:
            self.re_protocol = None

        try:
            self.re_method = re.compile(self.description['match']['method'])
        except:
            self.re_method = None

        try:
            self.re_host = re.compile(self.description['match']['host'])
        except:
            self.re_host = None

        try:
            self.re_raw_parameters = re.compile(self.description['match']['raw_parameters'])
        except:
            self.re_raw_parameters = None

        try:
            self.re_ip = re.compile(self.description['match']['ip'])
        except:
            self.re_ip = None

        #ToDo : implement match_headers(self, request)
        self.re_headers = []
        try:
            h = self.description['match']['headers']
        except:
            self.re_headers = None
        for header, value in h:
            try:
                self.re_headers.append((header, re.compile(value)))
            except:
                self.re_headers = None
                break

    def match_URL(self, request):
        if self.re_url is None:
            return True
        try:
            return bool(self.re_url.match(request.uri))
        except:
            return False

    def match_protocol(self, request):
        if self.re_protocol is None:
            return True
        try:
            return bool(self.re_protocol.match(request.protocol))
        except:
            return False

    def match_method(self, request):
        if self.re_method is None:
            return True
        try:
            return bool(self.re_method.match(request.method))
        except:
            return False

    def match_host(self, request):
        if self.re_host is None:
            return True
        try:
            return bool(self.re_host.match(request.hostname))
        except:
            return False

    def match_raw_parameters(self, request):
        if self.re_raw_parameters is None:
            return True
        try:
            if request.args is None:
                return bool(self.re_raw_parameters.match(""))
            else:
                return bool(self.re_raw_parameters.match(request.args))
        except:
            return False

    def match_ip(self, request):
        if self.re_ip is None:
            return True
        try:
            return bool(self.re_host.match(request.remote_ip))
        except:
            return False

    def match_headers(self, request):
        pass

    def match_parameters(self, request):
        pass

    # decorator dedicated to prepare request body to be read
    # and handled properly within the InputFilter
    # (or is this a design failure ?)
    def _can_read_body(self, request):
        if 'wl.must_not_read_body' in request.tags:
            return False
        else:
            return True
        # - read body if authorized
        # - let body content being re-attached to the request
        # - hook up proper input filter to handle body content
        # (request.add_input_filter(filter_name))
        pass

    def _read_body(self, request):
        if not self._can_read_body(request):
            return False
        if request.body is not None:
            return True
        request.body = request.read()
        return True

    def match_body_raw(request):
        pass

    def match_body_as_parameters(request):
        pass

    def match_body_as_json(request):
        pass

    def match_body_length(request):
        pass


class RequestAnalyzer(object):
    def __init__(self, request, rules):
        self.rules = rules
        self.request = request
        self.request.tags = set()

        if self.request.method is not None and len(self.request.method) != 0:
            self.tags.add(self.request.method)
        if self.request.protocol is not None:
            self.tags.add(self.request.protocol)
        if self.request.args is not None:
            self.tags.add('has_args')
        self.request.wl_continue_analysis = True
        self.request.wl_whitelisted = False


def handler(req):
    req.log_error('--------------- START OF HANDLER -----------------',
                  apache.APLOG_DEBUG)
    req.headers_in.add('X-wlister', 'TEST-WLISTER')
    req.headers_in.add('X-wlister', 'TEST2')
    req.log_error('request.the_request ' + str(req.the_request),
                  apache.APLOG_DEBUG)
    req.log_error('request.method ' + str(req.method),
                  apache.APLOG_DEBUG)
    req.log_error('request.protocol ' + str(req.protocol),
                  apache.APLOG_DEBUG)
    #req.log_error('request.range ' + str(req.range), apache.APLOG_DEBUG)
    req.log_error('request.unparsed_uri ' + str(req.unparsed_uri),
                  apache.APLOG_DEBUG)
    req.log_error('request.uri ' + str(req.uri),
                  apache.APLOG_DEBUG)
    req.log_error('request.range ' + str(req.range),
                  apache.APLOG_DEBUG)
    req.log_error('request.parsed_uri ' + str(req.parsed_uri),
                  apache.APLOG_DEBUG)
    req.log_error('request.args ' + str(req.args),
                  apache.APLOG_DEBUG)
    req.body = req.read()
    #req.notes.add('body', req.read())
    #req.log_error('request.body ' + str(req.body),
    #              apache.APLOG_DEBUG)
    req.log_error('req.main ' + str(req.main),
                  apache.APLOG_DEBUG)
    req.log_error('req.headers_in ' + str(req.headers_in),
                  apache.APLOG_DEBUG)
    req.log_error('req.headers_out ' + str(req.headers_out),
                  apache.APLOG_DEBUG)
    req.log_error('req.content_type ' + str(req.content_type),
                  apache.APLOG_DEBUG)
    req.uuid = uuid.uuid4()
    req.log_error('req.uuid ' + str(req.uuid),
                  apache.APLOG_DEBUG)
    req.log_error('req.get_options() ' + str(req.get_options()),
                  apache.APLOG_DEBUG)
    req.log_error('req.useragent_addr ' + str(req.connection.remote_ip),
                  apache.APLOG_DEBUG)

    try:
        req.content_length = int(req.headers_in['Content-Length'])
    except:
        req.content_length = 0
    req.log_error('req.content_length ' + str(req.content_length),
                  apache.APLOG_DEBUG)

    for h in req.headers_in:
        req.log_error(str(h) + ' - ' + str(req.headers_in[h]),
                      apache.APLOG_DEBUG)

    req.log_error('--------------- END OF HANDLER -----------------',
                  apache.APLOG_DEBUG)

    return apache.OK


def input_filter(filter):
    if filter.req.main is not None:
        filter.pass_on()
        filter.flush
        filter.close()
        return

    if not filter.is_input:
        return

    filter.req.log_error('--------------- START OF FILTER -----------------',
                         apache.APLOG_DEBUG)
    filter.req.log_error('req.uuid ' + str(filter.req.uuid),
                         apache.APLOG_DEBUG)
    # if there is a body content to forward...
    #if filter.req.body is not None:
    #    filter.write(filter.req.body)
    try:
        r = filter.read()
    except:
        r = None
    if r is not None:
        if len(r) > filter.req.content_length:
            filter.req.log_error('ALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARM!!!!',
                                 apache.APLOG_DEBUG)
    if r is not None:
        filter.write(r)
    filter.req.log_error('filter.read() "' + str(r) + '"',
                         apache.APLOG_DEBUG)
    filter.flush()
    filter.close()
    filter.req.log_error('--------------- END OF FILTER -----------------',
                         apache.APLOG_DEBUG)
    return apache.HTTP_NOT_FOUND
