# -*- coding: utf-8 -*-

import re


class WLRule(object):
    attributes = ('uri', 'protocol', 'method',
                  'host', 'args')

    def __init__(self, description, log=None):
        # list of method that must be used to validate a matching
        self.match_list = []
        self.prerequisite_list = []

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

        self.init_match()
        self.init_prerequisite()
        self.init_action_if_match()
        self.init_action_if_mismatch()

    def init_match(self):
        for attribute in self.attributes:
            self.init_match_attribute(attribute)
        # matching material and match_* functions registration
        self.init_match_headers()
        self.init_match_parameters()
        self.init_match_parameter()
        self.init_match_parameter_list()
        self.init_match_content_url_encoded()

    def init_match_attribute(self, attribute):
        try:
            c_regex = re.compile(self.description['match'][attribute])
        except KeyError:
            return
        except:
            self.log('Error compiling pattern - match:' +
                     str(attribute) + ':' +
                     self.description['match'][attribute] +
                     ' - skipping')

        def match_attribute(request, attr=attribute, c_reg=c_regex):
            try:
                if hasattr(request, attr):
                    return bool(c_reg.match(getattr(request, attr)))
                else:
                    self.log('Error - trying to access missing attribute '
                             + str(attr))
                    return False
            except Exception as e:
                self.log(str(id(self)) + ' raised exception - ' + str(e))
                return False
        if c_regex is not None:
            setattr(self, 'match_' + attribute, match_attribute)
            self.match_list.append('match_' + attribute)

    def init_match_parameters(self):
        self.re_parameters = []
        try:
            p = self.description['match']['parameters']
            for parameter, value in p:
                try:
                    self.re_parameters.append((parameter,
                                               re.compile(value)))
                except:
                    self.log('match:parameters regex compilation error - (' +
                             str(parameter) + ', ' +
                             str(value) + ') - skipping')
            self.match_list.append('match_parameters')
        except:
            self.re_parameters = None

    def match_parameters(self, request):
        # all parameters must match, exactly
        if self.re_parameters is None:
            return True
        if request.parameters is None:
            return False
        if len(request.parameters) != len(self.re_parameters):
            return False
        parameters = []
        for p, v in request.parameters:
            parameters.append([p, v, False])
        # iteration on self.re_parameters first ensure 1 pattern matches
        # only 1 parameter
        for name, re in self.re_parameters:
            for p in parameters:
                if p[2] is False and name == p[0] and re.match(p[1]):
                    p[2] = True
                    break
        return all([p[2] for p in parameters])

    def init_match_parameter(self):
        self.re_parameter = []
        if 'match' in self.description and \
                'parameter' in self.description['match']:
            try:
                parameter, value = self.description['match']['parameter']
                self.re_parameter = (parameter, re.compile(value))
            except:
                self.log('match:parameter regex compilation error - (' +
                         str(parameter) + ', ' +
                         str(value) + ') - skipping')
                self.re_parameter = None
            self.match_list.append('match_parameter')
        else:
            self.re_parameter = None

    def match_parameter(self, request):
        if self.re_parameter is None:
            return True
        if request.parameters is None:
            return False
        for p, v in request.parameters:
            if self.re_parameter[0] == p and \
                    self.re_parameter[1].match(v):
                return True
        return False

    def init_match_parameter_list(self):
        self.parameter_list = []
        if 'match' in self.description and \
                'parameter_list' in self.description['match']:
            if type(self.description['match']['parameter_list']) is list:
                self.parameter_list = \
                    self.description['match']['parameter_list']
                self.match_list.append('match_parameter_list')
            else:
                self.parameter_list = None
                self.log('ERROR - match:parameter_list is not a list - ' +
                         'rule is broken')
        else:
            self.parameter_list = None

    def match_parameter_list(self, request):
        if self.parameter_list is None:
            self.log('ERROR - match_parameter_list called while ' +
                     'parameter_list is None')
            return True
        if request.parameters is None:
            if len(self.parameter_list) == 0:
                return True
            else:
                return False
        if len(request.parameters) != len(self.parameter_list):
            return False
        parameters = []
        for p, v in request.parameters:
            parameters.append([p, False])
        for name in self.parameter_list:
            for p in parameters:
                if p[1] is False and \
                        p[0] == name:
                    p[1] = True
                    break
        return all([p[1] for p in parameters])

    def init_match_content_url_encoded(self):
        self.re_content_url_encoded = []
        try:
            #ToDo: Must trigger exception to many times and is to time
            # consuming. Change the way it is checked
            u = self.description['match']['content_url_encoded']
            for parameter, value in u:
                try:
                    self.re_content_url_encoded.append((parameter,
                                                        re.compile(value)))
                except:
                    self.log('match:content_url_encoded regex compilation ' +
                             'error - (' + str(parameter) + ', ' +
                             str(value) + ') - skipping')
            self.match_list.append('match_content_url_encoded')
        except:
            self.re_content_url_encoded = None

    def match_content_url_encoded(self, request):
        # all parameters must macth exactly
        if self.re_content_url_encoded is None:
            return True
        if request.content_url_encoded is None:
            return False
        if len(request.content_url_encoded) != \
                len(self.re_content_url_encoded):
            return False
        content_url_encoded = []
        for p, v in request.content_url_encoded:
            content_url_encoded.append([p, v, False])
        # iteration on self.re_parameters first ensure 1 pattern matches
        # only 1 parameter
        for name, re in self.re_content_url_encoded:
            for c in content_url_encoded:
                if c[2] is False and name == c[0] and re.match(c[1]):
                    c[2] = True
                    break
        return all([c[2] for c in content_url_encoded])

    def init_match_headers(self):
        self.re_headers = []
        try:
            #ToDo: Must trigger exception to many times and is too time
            # consuming. Change the way it is checked
            h = self.description['match']['headers']
            for header, value in h:
                try:
                    self.re_headers.append((header, re.compile(value)))
                except:
                    self.log('Regex compilation error (' +
                             str(header) + ', ' + str(value) +
                             ') - skipping')
            self.match_list.append('match_headers')
        except:
            self.re_headers = None

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

    def init_prerequisite(self):
        # list of method that must be used to validate prerequisites
        self.prerequisite_list = []
        # prerequisites material and prerequisites_* function registration
        self.has_tag = None
        self.has_not_tag = None
        if 'prerequisite' not in self.description:
            return
        if 'has_tag' in self.description['prerequisite']:
            if type(self.description['prerequisite']['has_tag']) is list:
                self.has_tag = self.description['prerequisite']['has_tag']
            else:
                self.has_tag = [self.description['prerequisite']['has_tag']]
            self.prerequisite_list.append('prerequisite_has_tag')

        if 'has_not_tag' in self.description['prerequisite']:
            if type(self.description['prerequisite']['has_not_tag']) is list:
                self.has_not_tag = \
                    self.description['prerequisite']['has_not_tag']
            else:
                self.has_not_tag = \
                    [self.description['prerequisite']['has_not_tag']]
            self.prerequisite_list.append('prerequisite_has_not_tag')

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

    # main match function
    # other match_* functions are not meant to be called
    def match(self, request):
        return all([getattr(self, m)(request)
                    for m in self.match_list])

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
        return all([getattr(self, p)(request)
                    for p in self.prerequisite_list])

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
        for action in self.action_if_match_list:
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
        for action in self.action_if_mismatch_list:
            getattr(self, action)(request)

    def analyze(self, request):
        if not self.prerequisite(request):
            return
        if self.match(request):
            self.action_if_match(request)
        else:
            self.action_if_mismatch(request)
