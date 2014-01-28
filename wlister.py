# -*- coding: utf-8 -*-

from mod_python import apache

apache.wl_rules = None
apache.wl_config = None

apache.log_error('WLISTER Imported', apache.APLOG_CRIT)

import re
import json


def log(message, log_level=None):
    try:
        apache.log_error(apache.wl_config['wlister.log_prefix'] +
                         ' ' + message, apache.APLOG_CRIT)
    except:
        apache.log_error(message, apache.APLOG_CRIT)


# ToDo: put init_wlister into this function !
def init_wlister(request):
    """
    Initialize wlister parameters from apache configuration
    Paramaters are:
        - wlister.log_prefix: prefix to prepend to wlister log entries
        - wlister.default_action: default action at the end of rules testing
        when no directive applied (see WLRules.action_if_match* and
        WLRules.action_if_mismatch*)
        - wlister.conf: file path describing the rules to be applied
    """
    if apache.wl_config is not None:
        return True
    apache.wl_config = {}
    apache.wl_rules = []
    options = request.get_options()

    try:
        apache.wl_config['wlister.log_prefix'] = options['wlister.log_prefix']
    except:
        apache.wl_config['wlister.log_prefix'] = '[wlister]'

    try:
        if options['wlister.default_action'] in ['block', 'pass', 'learn']:
            apache.wl_config['wlister.default_action'] = \
                options['wlister.default_action']
        else:
            apache.wl_config['wlister.default_action'] = 'block'
            log('unknown value for wlister.default_action (lock, pass, learn)')
            log('default action is ' +
                apache.wl_config['wlister.default_action'])
    except:
        apache.wl_config['wlister.default_action'] = 'block'
        log('wlister.default_action not defined')
        log('default action is ' +
            apache.wl_config['wlister.default_action'])

    try:
        apache.wl_config['wlister.conf'] = options['wlister.conf']
    except:
        apache.wl_config['wlister.conf'] = None
        log('wlister.conf is not set - can not analyze request')

    if apache.wl_config['wlister.conf'] is not None:
        f = None
        try:
            f = open(apache.wl_config['wlister.conf'])
        except:
            log('Can not open configuration file (wlister.conf) - ' +
                str(apache.wl_config['wlister.conf']))
        if f is not None:
            d = None
            try:
                d = json.load(f)
            except Exception as e:
                log('Rules format is not json compliant - ' +
                    str(apache.wl_config['wlister.conf']) +
                    str(e))
            if d is not None:
                for r in d:
                    apache.wl_rules.append(WLRule(r))
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
        self.init_match()
        self.init_prerequisite()
        self.init_action_if_match()
        self.init_action_if_mismatch()

    def init_match(self):
        # list of method that must be used to validate a matching
        self.match_list = []
        # matching material and match_* functions registration
        self.init_match_url()
        self.init_match_protocol()
        self.init_match_method()
        self.init_match_host()
        self.init_match_ip()
        self.init_match_raw_parameters()
        self.init_match_headers()
        self.init_match_parameters()

    def init_match_url(self):
        try:
            self.re_url = re.compile(self.description['match']['url'])
            self.match_list.append('match_URL')
        except:
            self.re_url = None

    def init_match_protocol(self):
        try:
            self.re_protocol = \
                re.compile(self.description['match']['protocol'])
            self.match_list.append('match_protocol')
        except:
            self.re_protocol = None

    def init_match_method(self):
        try:
            self.re_method = \
                re.compile(self.description['match']['method'])
            self.match_list.append('match_method')
        except:
            self.re_method = None

    def init_match_host(self):
        try:
            self.re_host = re.compile(self.description['match']['host'])
            self.match_list.append('match_host')
        except:
            self.re_host = None

    def init_match_ip(self):
        try:
            self.re_ip = re.compile(self.description['match']['ip'])
            self.match_list.append('match_ip')
        except:
            self.re_ip = None

    def init_match_raw_parameters(self):
        try:
            self.re_raw_parameters = \
                re.compile(self.description['match']['raw_parameters'])
            self.match_list.append('match_raw_parameters')
        except:
            self.re_raw_parameters = None

    def init_match_parameters(self):
        self.re_parameters = []
        try:
            p = self.description['match']['parameters']
            for parameter, value in p:
                try:
                    self.re_parameters.append((parameter,
                                               re.compile(value)))
                except:
                    log('match:parameters regex compilation error - (' +
                        str(parameter) + ', ' + str(value) + ') - skipping')
            self.match_list.append('match_parameters')
        except:
            self.re_parameters = None

    def init_match_headers(self):
        self.re_headers = []
        try:
            h = self.description['match']['headers']
            for header, value in h:
                try:
                    self.re_headers.append((header, re.compile(value)))
                except:
                    apache.log_error('Regex compilation error (' +
                                     str(header) + ', ' + str(value) +
                                     ') - skipping', apache.APLOG_ERR)
            self.match_list.append('match_headers')
        except:
            self.re_headers = None

    def init_prerequisite(self):
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

    def init_action_if_match(self):
        # list of methodes that must be used if matching is validated
        self.action_if_match_list = []
        # if_match material and if_match_* function registration
        try:
            self.if_match_set_tag = \
                self.description['action_if_match']['set_tag']
            if type(self.if_match_set_tag) is not list:
                self.if_match_set_tag = [self.if_match_set_tag]
            self.action_if_match_list.append('action_if_match_set_tag')
        except:
            self.if_match_set_tag = None

        try:
            self.if_match_unset_tag = \
                self.description['action_if_match']['unset_tag']
            if type(self.if_match_unset_tag) is not list:
                self.if_match_unset_tag = [self.if_match_unset_tag]
            self.action_if_match_list.append['action_if_match_unset_tag']
        except:
            self.if_match_unset_tag = None

        try:
            self.if_match_whitelist = \
                self.description['action_if_match']['whitelist']
            self.action_if_match_list.append('action_if_match_whitelist')
        except:
            self.if_match_whitelist = None

        try:
            self.if_match_blacklist = \
                self.description['action_if_match']['blacklist']
            self.action_if_match_list.append('action_if_match_blacklist')
        except:
            self.if_match_blacklist = None

    def init_action_if_mismatch(self):
        # list of methods that must be used if matching is not validated
        self.action_if_mismatch_list = []
        # if_mismatch material and if_mismatch_* function registration
        try:
            self.if_mismatch_set_tag = \
                self.description['action_if_mismatch']['set_tag']
            if type(self.if_mismatch_set_tag) is not list:
                self.if_mismatch_set_tag = [self.if_mismatch_set_tag]
            self.action_if_mismatch_list.append('action_if_mismatch_set_tag')
        except:
            self.if_mismatch_set_tag = None

        try:
            self.if_mismatch_unset_tag = \
                self.description['action_if_mismatch']['unset_tag']
            if type(self.if_mismatch_unset_tag) is not list:
                self.if_mismatch_unset_tag = [self.if_mismatch_unset_tag]
            self.action_if_mismatch_list.append('action_if_mismatch_unset_tag')
        except:
            self.if_mismatch_unset_tag = None

        try:
            self.if_mismatch_whitelist = \
                self.description['action_if_mismatch']['whitelist']
            self.action_if_mismatch_list.append('action_if_mismatch_whitelist')
        except:
            self.if_mismatch_whitelist = None

        try:
            self.if_mismatch_blacklist = \
                self.description['action_if_mismatch']['blacklist']
            self.action_if_mismatch_list.append('action_if_mismatch_blacklist')
        except:
            self.if_mismatch_blacklist = None

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

    def match_parameters(self, request):
        # all parameters must match, exctly
        if self.re_parameters is None:
            return True
        if request.wl_parameters is None:
            return False
        if len(request.wl_parameters) != len(self.re_parameters):
            return False
        parameters = []
        for p, v in request.wl_parameters:
            parameters.append([p, v, False])
        # iteration on self.re_parameters first ensure 1 pattern matches
        # only 1 parameter
        for name, re in self.re_parameters:
            for p in parameters:
                if p[2] is False and name == p[0] and re.match(p[1]):
                    p[2] = True
                    break
        return all([p[2] for p in parameters])

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

    # main match function - other match_* functions are not to be called
    def match(self, request):
        return all([getattr(self, m)(request)
                    for m in self.match_list])

    def prerequisite_has_tag(self, request):
        if self.has_tag is None:
            return True
        has_tag = True
        for tag in self.has_tag:
            if tag not in request.wl_tags:
                has_tag = False
                break
        return has_tag

    def prerequisite_has_not_tag(self, request):
        if self.has_not_tag is None:
            return True
        has_not_tag = True
        for tag in self.has_not_tag:
            if tag in request.wl_tags:
                has_not_tag = False
                break
        return has_not_tag

    # main prerequisite validator
    def prerequisite(self, request):
        return all([getattr(self, p)(request)
                    for p in self.prerequisite_list])

    def action_if_match_set_tag(self, request):
        if self.if_match_set_tag is None:
            return
        for t in self.if_match_set_tag:
            request.wl_tags.add(t)

    def action_if_match_unset_tag(self, request):
        if self.if_match_unset_tag is None:
            return
        for t in self.if_match_unset_tag:
            request.wl_tags.discard(t)

    def action_if_match_whitelist(self, request):
        if self.if_match_whitelist is None:
            request.wl_whitelisted = False
            return
        if self.if_match_whitelist == 'True':
            request.wl_whitelisted = True
            return
        if self.if_match_whitelist == 'False':
            request.wl_whitelisted = False
            return

    def action_if_match_blacklist(self, request):
        if self.if_match_blacklist is None:
            request.wl_blacklisted = False
            return
        if self.if_match_blacklist == 'True':
            request.wl_blacklisted = True
            return
        if self.if_match_blacklist == 'False':
            request.wl_blacklisted = False
            return

    # main action_if_match hook
    def action_if_match(self, request):
        for action in self.action_if_match_list:
            getattr(self, action)(request)

    def action_if_mismatch_set_tag(self, request):
        if self.if_mismatch_set_tag is None:
            return
        for t in self.if_mismatch_set_tag:
            request.wl_tags.add(t)

    def action_if_mismatch_unset_tag(self, request):
        if self.if_mismatch_unset_tag is None:
            return
        for t in self.if_mismatch_unset_tag:
            request.wl_tags.discard(t)

    def action_if_mismatch_whitelist(self, request):
        if self.if_mismatch_whitelist is None:
            request.wl_whitelisted = False
            return
        if self.if_mismatch_whitelist == 'True':
            request.wl_whitelisted = True
            return
        if self.if_mismatch_whitelist == 'False':
            request.wl_whitelisted = False
            return

    def action_if_mismatch_blacklist(self, request):
        if self.if_mismatch_blacklist is None:
            request.wl_blacklisted = False
            return
        if self.if_mismatch_blacklist == 'True':
            request.wl_blacklisted = True
            return
        if self.if_mismatch_blacklist == 'False':
            request.wl_blacklisted = False
            return

    # main action_if_mismatch hook
    def action_if_mismatch(self, request):
        for action in self.action_if_mismatch_list:
            getattr(self, action)(request)

    def analyze(self, request):
        if not self.prerequisite(request):
            return
        if self.match(request):
            self.action_if_match(request)
        else:
            self.action_if_mismatch(request)


def request_init(request):
    request.wl_tags = set()
    request.wl_whitelisted = False
    request.wl_blacklisted = False

    # dealing with parameters
    if request.args is not None:
        request.wl_tags.add('wl.has_parameters')
        request.wl_parameters = [arg.split('=', 1)
                                 for arg in request.args.split('&')]
        for parameter in request.wl_parameters:
            if len(parameter) == 1:
                parameter.append('')
    else:
        request.wl_parameters = None

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
    init_wlister(req)

    for rule in apache.wl_rules:
        rule.analyze(req)
        if req.wl_whitelisted:
            return apache.OK
        if req.wl_blacklisted:
            return apache.HTTP_NOT_FOUND

    default_action = apache.wl_config['wlister.default_action']
    if default_action == 'block':
        return apache.HTTP_NOT_FOUND
    elif default_action == 'pass':
        return apache.OK

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
