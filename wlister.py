# -*- coding: utf-8

from mod_python import apache
apache.wl_rules = None

apache.log_error('WLISTER Imported', apache.APLOG_ERR)

import re
import json

def init_wlister(path):
    try:
        f = open(path)
    except:
        apache.log_error('Can not open configuration file - ' +
                         str(path), apache.APLOG_ERR)
        return False
    try:
        d = json.load(f)
    except Exception as e:
        apache.log_error('Rules format is not json compliant - ' +
                         str(path) + ' - ' + str(e),
                         apache.APLOG_ERR)
        return False

    if apache.wl_rules is None:
        apache.wl_rules = {}

    if path in apache.wl_rules.keys():
        return True

    apache.wl_rules[path] = []
    for r in d:
        apache.wl_rules[path].append(WLRule(r))
    return True

# Example of Rule format
#rules = [
#    {
#        "id": "000000",
#        "match":
#        {
#            "url": "^/\d+/\d+$",
#            "protocol": "^HTTP/1\.1$",
#            "method": "^GET$",
#            "host": "^mapom.me$",
#            "raw_parameters": "^$",
#            "ip": "^127\.0\.0\.1$",
#            "headers":
#            {
#                "Content-Type": "^application/x-www-form-urlencoded$",
#                "Host": "^mapom.me$"
#            }
#        },
#        "prerequisites":
#        {
#            "has_tag": ["tag01", "tag02"]
#        },
#        "actions_if_match":
#        {
#            "set_tag": ["tag03", "tag04"],
#            "unset_tag": ["tag01"],
#            "set_whitelisted": True
#        },
#        "actions_if_mismatch":
#        {
#            "set_tag": ["blah", "blih"]
#        }
#    }
#]


class WLRule(object):
    def __init__(self, description):
        if type(description) is not dict:
            raise TypeError("Description parameter must be a dictionary")
        self.description = description

        # list of method that must be used to validate a matching
        self.match_list = []

        # matching material and match_* functions registration
        try:
            self.re_url = re.compile(self.description['match']['url'])
            self.match_list.append('match_URL')
        except:
            self.re_url = None

        try:
            self.re_protocol = re.compile(self.description['match']['protocol'])
            self.match_list.append('match_protocol')
        except:
            self.re_protocol = None

        try:
            self.re_method = re.compile(self.description['match']['method'])
            self.match_list.append('match_method')
        except:
            self.re_method = None

        try:
            self.re_host = re.compile(self.description['match']['host'])
            self.match_list.append('match_host')
        except:
            self.re_host = None

        try:
            self.re_ip = re.compile(self.description['match']['ip'])
            self.match_list.append('match_ip')
        except:
            self.re_ip = None

        try:
            self.re_raw_parameters = re.compile(self.description['match']['raw_parameters'])
            self.match_list.append('match_raw_parameters')
        except:
            self.re_raw_parameters = None

        self.re_headers = []
        try:
            h = self.description['match']['headers']
            for header, value in h:
                try:
                    self.re_headers.append((header, re.compile(value)))
                except:
                    apache.log_error('Regex compilation error (' + str(header)
                                     + ', ' + str(value) + ') - skipping',
                                     apache.APLOG_ERR)
            self.match_list.append('match_headers')
        except:
            self.re_headers = None

        # list of method that must be used to validate prerequisites
        self.prerequisite_list = []
        # prerequisites material and prerequisites_* function registration
        try:
            self.has_tag = self.description['prerequisite']['has_tag']
            self.prerequisite_list.append('prerequisite_has_tag')
        except:
            self.has_tag = None

        try:
            self.has_not_tag = self.description['prerequisite']['has_not_tag']
            self.prerequisite_list.append('prerequisite_has_not_tag')
        except:
            self.has_not_tag = None

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

    def match_ip(self, request):
        if self.re_ip is None:
            return True
        try:
            return bool(self.re_host.match(request.remote_ip))
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

    # ToDo: change function so that it can handle the
    # double header behavior that provides tuple instead of string
    def match_headers(self, request):
        if self.re_headers is None:
            return True
        match = True
        for header, re_value in self.re_headers:
            # Todo: use header in r.headers_in statement
            try:
                m = re_value.match(request.headers_in[header])
                if m is None:
                    match = False
            except:
                match = False
            if match is False:
                break
        return match

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

    def analyze(self, request):
        pass


def request_init(request):
    request.wl_tags = set()
    request.wl_whitelisted = False

    # dealing with parameters
    if request.args is not None:
        request.wl_tags.add('wl.has_parameters')
        request.parameters = [arg.split('=', 1)
                              for arg in request.args.split('&')]
        for parameter in request.parameters:
            if len(parameter) == 1:
                parameter.append('')

    # dealing with method
    if request.method is not None:
        request.wl_tags.add('wl.method.' + str(request.method).lower())
    else:
        request.wl_tags.add('wl.method.None')

    # dealing with content-length if any
    if 'Content-Length' in request.headers_in:
        request.wl_tags.add('wl.has_body')


def handler(req):
    request_init(req)

    try:
        config = req.get_options()['wlister.conf']
    except:
        apache.log_error('Can not find PythonOption: wlister.conf \
                         - can not analyze request',
                         apache.APLOG_CRIT)
        return apache.DECLINED

    if not init_wlister(config):
        apache.log_error('Can not process request without configuration',
                         apache.APLOG_CRIT)
        return apache.DECLINED

    for rule in apache.wl_rules[config]:
        pass

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
