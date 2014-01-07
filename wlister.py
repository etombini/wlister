# -*- coding: utf-8

from mod_python import apache

import uuid
import re

rules = [
    {
        "id": "000000",
        "url": "^/\d+/\d+$",
        "prerequisites":
        {
            "has_tag": ["tag01", "tag02"]
        },
        "actions":
        {
            "set_tag": ["tag03", "tag04"],
            "unset_tag": ["tag01"]
        }
    }
]


class WLSignature(object):
    def __init__(self, description):
        if type(description) is not dict:
            raise TypeError("Description parameter must be a dictionary")
        try:
            self.url = re.compile(description['url'])
        except:
            self.url = None


class RequestAnalyzer(object):
    def __init__(self, request, rules):
        self.rules = rules
        self.request = request
        self.tags = set()

        if self.request.method is not None and len(self.request.method) != 0:
            self.tags.add(self.request.method)
        if self.request.protocol is not None:
            self.tags.add(self.request.protocol)
        if self.request.args is not None:
            self.tags.add('has_args')


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
    req.log_error('request.uri[2] ' + str(req.uri[2]),
                  apache.APLOG_DEBUG)
    req.log_error('request.parsed_uri ' + str(req.parsed_uri),
                  apache.APLOG_DEBUG)
    req.log_error('request.args ' + str(req.args),
                  apache.APLOG_DEBUG)
    req.body = req.read()
    req.log_error('req.main ' + str(req.main),
                  apache.APLOG_DEBUG)
    req.log_error('req.headers_in ' + str(req.headers_in),
                  apache.APLOG_DEBUG)
    req.log_error('req.headers_out ' + str(req.headers_out),
                  apache.APLOG_DEBUG)
    req.uuid = uuid.uuid4()
    req.log_error('req.uuid ' + str(req.uuid),
                  apache.APLOG_DEBUG)
    req.log_error('req.get_options() ' + str(req.get_options()),
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

    if req.uri[2] == "2":
        req.content_type = 'text/plain'
        req.write('you have selected 2 !!!!')
        return apache.DONE
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
    if filter.req.body is not None:
        filter.write(filter.req.body)
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
