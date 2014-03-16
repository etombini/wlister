# -*- coding: utf-8 -*-

import os

class WLRequest(object):
    def __init__(self, request, log=None, max_content_length=1024):
        self.request = request
        if log is None:
            self.log = self.log_nothing
        else:
            self.log = log
        self.max_content_length = max_content_length
        self.content_length = 0
        self.content = ''
        self.tags = set()
        self.whitelisted = False
        self.blacklisted = False

        self.init_method()
        self.init_parameters()
        self.init_body_content()
        self.init_body_content_type()

    def __repr__(self):
        return '<WLRequest %s>' % self.request.the_request

    def log_nothing(self, message):
        pass

    def __getattr__(self, key):
        if key in ['uri', 'protocol', 'method', 'host', 'args']:
            return getattr(self.request, key)
        else:
            raise AttributeError(key)

    def init_method(self):
        if self.request.method is None:
            self.tags.add('wl.method.None')
        else:
            self.tags.add('wl.method.' + str(self.request.method).lower())

    def init_parameters(self):
        # dealing with parameters
        if self.request.args is not None:
            self.tags.add('wl.has_parameters')
            self.parameters = [arg.split('=', 1)
                               for arg in self.request.args.split('&')]
            for parameter in self.parameters:
                if len(parameter) == 1:
                    parameter.append('')
        else:
            self.parameters = None

    def init_body_content(self):
        # dealing with content-length if any
        if 'Content-Length' in self.request.headers_in:
            self.tags.add('wl.has_body')
            self.content_length = \
                int(self.request.headers_in['Content-Length'])
        else:
            self.content_length = 0
            self.max_content_length = 0
            return

        if self.content_length > self.max_content_length:
            self.log('request body length (' +
                     str(self.request.headers_in['Content-Length']) +
                     ') is greater than wlister.max_post_read (' +
                     str(self.max_content_length) + ') - skipping body analyis')
            return
        elif self.content_length > 0:
            try:
                self.content = self.request.read(self.content_length)
                current_path = os.path.dirname(os.path.abspath(__file__))
                self.request.register_input_filter('wlister_pass_filter',
                                                   'wlister::input_filter',
                                                   current_path)
                self.request.add_input_filter('wlister_pass_filter')
                #self.content = self.request.read(self.content_length)
                self.log('READING ' + str(self.content_length) + ' bytes')
                self.log('CONTENT IS ' + str(self.content))
                # Required to forward content when applying input filter
                self.request.body = self.content
            except IOError:
                self.log('reading request body failed' +
                         ' - TimeOut may be reached - ' +
                         'request processing is unknown')
            except Exception as e:
                self.log('WHAT IS THAT ? ' + str(e))
        else:
            self.tags.add('wl.bad_content_length')

    def init_body_content_type(self):
        if self.content_length == 0:
            return
        if 'Content-Type' not in self.request.headers_in:
            return
        if self.request.headers_in['Content-Type'] == \
                'application/x-www-form-urlencoded':
            self.content_url_encoded = \
                [arg.split('=', 1) for arg in self.content.split('&')]
            for p in self.content_url_encoded:
                if len(p) == 1:
                    p.append('')
            return
        else:
            self.content_url_encoded = None
        if self.request.headers_in['Content-Type'] == \
                'application/json':
            try:
                import json
                self.content_json = json.loads(self.content)
            except:
                self.log('can not load JSON content - json.loads() failed')
            return
        else:
            self.content_json = None
