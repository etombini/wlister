# -*- coding: utf-8 -*-

import re


class WLRule(object):
    attributes = ('uri', 'protocol', 'method',
                  'host', 'args')

    def __init__(self, description, log=None):
        # list of method that must be used to validate a matching
        self.match_register = []
        self.prerequisite_register = []
        self.action_if_match_register = []
        self.action_if_mismatch_register = []

        if 'id' in description:
            self._id = description['id']
        else:
            self._id = id(self)

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

        self.register_prerequisite()
        self.register_match()
        self.init_action_if_match()
        self.init_action_if_mismatch()

    def register_match(self):
        if 'match' not in self.description:
            return
        for attribute in self.attributes:
            self.register_match_attribute(attribute)
        # matching material and match_* functions registration
        self.register_match_parameters()
        self.register_match_headers()
        # self.register_match_content_url_encoded()

        self.init_match_parameter()

        self.register_match_parameters_list()
        self.register_match_headers_list()
        self.register_match_content_url_encoded_list()

        self.init_match_content_url_encoded()

    def register_match_attribute(self, attribute):
        if attribute not in self.description['match']:
            return
        try:
            c_regex = re.compile(self.description['match'][attribute])
        except Exception as e:
            self.log('ERROR - register_match_attribute(' +
                     str(attribute) + ') - ' +
                     ' Cannot compile regex: ' +
                     str(self.description['match'][attribute]) +
                     ' - ' + str(e))

        def match_attribute(request, attr=attribute, c_reg=c_regex):
            try:
                if hasattr(request, attr) and \
                        getattr(request, attr) is not None:
                    return bool(c_reg.match(getattr(request, attr)))
                else:
                    self.log('Error - trying to access missing attribute '
                             + str(attr))
                    return False
            except Exception as e:
                self.log(str(id(self)) + ' ' + str(attr) + ' ' +
                         str(getattr(request, attr)) +
                         ' raised exception - ' + str(e))
                return False
        if c_regex is not None:
            setattr(self, 'match_' + attribute, match_attribute)
            self.match_register.append('match_' + attribute)

    # stands for register_match_(parameters|headers|content_url_encoded)
    def _register_match_items(self, items):
        if items not in self.description['match']:
            # Silently discard
            return
        if items not in ['parameters', 'headers', 'content_url_encoded']:
            self.log('ERROR - ' + str(self._id) + ' - ' + str(items) +
                     ' is not a referenced match (parameters, headers, content_url_encoded)')
            return
        setattr(self, 're_' + items, [])
        re_items = getattr(self, 're_' + items)
        p = sorted(self.description['match'][items],
                   key=lambda p: p[0])
        for name, value in p:
            try:
                re_items.append((name, re.compile(value)))
            except Exception as e:
                self.log('ERROR - match:' + str(items) + ' regex compilation error - ' +
                         '(' + str(name) + ', ' + str(value) + ') - skipping - ' +
                         str(e))
        self.match_register.append('match_' + items)

    def register_match_parameters(self):
        self._register_match_items('parameters')

    def register_match_headers(self):
        self._register_match_items('headers')

    def register_match_content_url_encoded(self):
        self._register_match_items('content_url_encoded')

    def _match_items(self, request, items):
        if getattr(request, items) is None:
            return False
        l = getattr(request, items)
        re_l = getattr(self, 're_' + items)
        if items == 'headers':
            self.log('DEBUG: _match_items for headers: ' +
                     str(l) + ' ' + str(re_l))
        if len(l) != len(re_l):
            return False
        # l and re_l are sorted
        for i in range(0, len(l)):
            if l[i][0] != re_l[i][0]:
                return False
            if not re_l[i][1].match(l[i][1]):
                return False
        return True

    def match_parameters(self, request):
        return self._match_items(request, 'parameters')

    def match_headers(self, request):
        return self._match_items(request, 'headers')

    def match_content_url_encoded(self, request):
        return self._match_items(request, 'content_url_encoded')

    def _register_match_items_in(self, items):
        if items + '_in' not in self.description['match']:
            # Silently discard
            return
        if items not in ['parameters', 'headers', 'content_url_encoded']:
            self.log('ERROR - ' + str(self._id) + ' - ' + str(items) +
                     ' is not a referenced match_in' +
                     ' (parameters_in, headers_in, content_url_encoded_in)')
            return
        setattr(self, 're_' + items + '_in', [])
        re_items_in = getattr(self, 're_' + items + '_in')
        p = sorted(self.description['match'][items + '_in'],
                   key=lambda p: p[0])
        for name, value in p:
            try:
                re_items_in.append((name, re.compile(value)))
            except Exception as e:
                self.log('ERROR - match:' + str(items) + '_in regex compilation error - ' +
                         '(' + str(name) + ', ' + str(value) + ') - skipping - ' +
                         str(e))
        self.match_register.append('match_' + items + '_in')

    def register_match_parameters_in(self):
        self._register_match_items_in('parameters')

    def register_match_headers_in(self):
        self._register_match_items_in('headers')

    def register_match_content_url_encoded_in(self):
        self._register_match_items_in('content_url_encoded')

    # This may not work if you have several times the same
    # parameter name with values that can not be matched by the
    # proper regex (e.g var1=val1&var1=!()%34 vs "^val\\d")
    def _match_items_in(self, request, items):
        if getattr(request, items) is None:
            return False
        l = getattr(request, items)
        re_l = getattr(self, 're_' + items + '_in')
        idx_re_l = 0
        for i in range(0, len(l)):
            if l[i][0] != re_l[idx_re_l]:
                continue
            if re_l[idx_re_l].match(l[i][1]):
                idx_re_l = idx_re_l + 1
            else:  # name is ok but value doesn't match
                return False
        return idx_re_l == len(re_l)

    def match_parameters_in(self, request):
        return self._match_items_in(request, 'parameters')

    def match_headers_in(self, request):
        return self._match_items_in(request, 'headers')

    def match_content_url_encoded_in(self, request):
        return self.match_items_in(request, 'content_url_encoded')

    def _register_match_items_list(self, items):
        if items + '_list' not in self.description['match']:
            # Silently discard
            return
        if items not in ['parameters', 'headers', 'content_url_encoded']:
            self.log('ERROR - ' + str(self._id) + ' - ' + str(items) +
                     ' is not a referenced match_list' +
                     ' (parameters_list, headers_list, content_url_encoded_list)')
            return
        if type(self.description['match'][items + '_list']) is not list:
            self.log('ERROR - ' + str(self._id) + ' - ' + str(items) +
                     '_list is not a list - skipping')
            return
        setattr(self, 're_' + items + '_list', self.description['match'][items + '_list'])
        self.match_register.append('match_' + items + '_list')

    def register_match_parameters_list(self):
        self._register_match_items_list('parameters')

    def register_match_headers_list(self):
        self._register_match_items_list('headers')

    def register_match_content_url_encoded_list(self):
        self._register_match_items_list('content_url_encoded')

    def _match_items_list(self, request, items):
        if getattr(request, items) is None:
            return False
        request_items = [name for name, value in getattr(request, items)]
        self.log('DEBUG - request.' + items + '_list ' + str(request_items))
        self.log('DEBUG - rule.re_' + items + '_list ' + str(getattr(self, 're_' + items + '_list')))
        # lists are sorted
        return request_items == getattr(self, 're_' + items + '_list')

    def match_parameters_list(self, request):
        self.log('DEBUG - match_parameters_list: starting')
        return self._match_items_list(request, 'parameters')

    def match_headers_list(self, request):
        return self._match_items_list(request, 'headers')

    def match_content_url_encoded_list(self, request):
        return self._match_items_list(request, 'content_url_encoded')

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
            self.match_register.append('match_parameter')
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

#    def init_match_parameter_list(self):
#        self.parameter_list = []
#        if 'match' in self.description and \
#                'parameter_list' in self.description['match']:
#            if type(self.description['match']['parameter_list']) is list:
#                self.parameter_list = \
#                    sorted(self.description['match']['parameter_list'],
#                           key=lambda p: p[0])
#                self.match_register.append('match_parameter_list')
#            else:
#                self.parameter_list = None
#                self.log('ERROR - match:parameter_list is not a list - ' +
#                         'rule is broken')
#        else:
#            self.parameter_list = None
#
#    def match_parameter_list(self, request):
#        if self.parameter_list is None:
#            self.log('ERROR - match_parameter_list called while ' +
#                     'parameter_list is None')
#            return True
#        if request.parameters is None:
#            return len(self.parameter_list) == 0
#        if len(request.parameters) != len(self.parameter_list):
#            return False
#        return request.parameter_list == \
#            sorted(self.parameter_list)

    def init_match_content_url_encoded(self):
        self.re_content_url_encoded = []
        try:
            u = self.description['match']['content_url_encoded']
            for parameter, value in u:
                try:
                    self.re_content_url_encoded.append((parameter,
                                                        re.compile(value)))
                except:
                    self.log('match:content_url_encoded regex compilation ' +
                             'error - (' + str(parameter) + ', ' +
                             str(value) + ') - skipping')
            self.match_register.append('match_content_url_encoded')
        except:
            self.re_content_url_encoded = None

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

    def init_action_if_match(self):
        # list of methodes that must be used if matching is validated
        self.action_if_match_register = []
        # if_match material and if_match_* function registration
        try:
            self.if_match_set_tag = \
                self.description['action_if_match']['set_tag']
            if type(self.if_match_set_tag) is not list:
                self.if_match_set_tag = [self.if_match_set_tag]
            self.action_if_match_register.append('action_if_match_set_tag')
        except:
            self.if_match_set_tag = None

        try:
            self.if_match_unset_tag = \
                self.description['action_if_match']['unset_tag']
            if type(self.if_match_unset_tag) is not list:
                self.if_match_unset_tag = [self.if_match_unset_tag]
            self.action_if_match_register.append['action_if_match_unset_tag']
        except:
            self.if_match_unset_tag = None

        try:
            self.if_match_whitelist = \
                self.description['action_if_match']['whitelist']
            self.action_if_match_register.append('action_if_match_whitelist')
        except:
            self.if_match_whitelist = None

        try:
            self.if_match_blacklist = \
                self.description['action_if_match']['blacklist']
            self.action_if_match_register.append('action_if_match_blacklist')
        except:
            self.if_match_blacklist = None

    def init_action_if_mismatch(self):
        # list of methods that must be used if matching is not validated
        self.action_if_mismatch_register = []
        # if_mismatch material and if_mismatch_* function registration
        try:
            self.if_mismatch_set_tag = \
                self.description['action_if_mismatch']['set_tag']
            if type(self.if_mismatch_set_tag) is not list:
                self.if_mismatch_set_tag = [self.if_mismatch_set_tag]
            self.action_if_mismatch_register.append('action_if_mismatch_set_tag')
        except:
            self.if_mismatch_set_tag = None

        try:
            self.if_mismatch_unset_tag = \
                self.description['action_if_mismatch']['unset_tag']
            if type(self.if_mismatch_unset_tag) is not list:
                self.if_mismatch_unset_tag = [self.if_mismatch_unset_tag]
            self.action_if_mismatch_register.append('action_if_mismatch_unset_tag')
        except:
            self.if_mismatch_unset_tag = None

        try:
            self.if_mismatch_whitelist = \
                self.description['action_if_mismatch']['whitelist']
            self.action_if_mismatch_register.append('action_if_mismatch_whitelist')
        except:
            self.if_mismatch_whitelist = None

        try:
            self.if_mismatch_blacklist = \
                self.description['action_if_mismatch']['blacklist']
            self.action_if_mismatch_register.append('action_if_mismatch_blacklist')
        except:
            self.if_mismatch_blacklist = None

    # main match function
    # other match_* functions are not meant to be called
    def match(self, request):
        for f in self.match_register:
            if not getattr(self, f)(request):
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
        for action in self.action_if_match_register:
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
        for action in self.action_if_mismatch_register:
            getattr(self, action)(request)

    def analyze(self, request):
        if not self.prerequisite(request):
            return
        if self.match(request):
            self.action_if_match(request)
        else:
            self.action_if_mismatch(request)
