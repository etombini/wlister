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

import os
import json


class WLRequest(object):
    def __init__(self, request, log=None, max_content_length=1024):
        self.request = request
        if log is None:
            self.log = self.log_nothing
        else:
            self.log = log
        self.max_content_length = max_content_length

        self.lazy = ['request_id',
                     'parameters',
                     'parameter_list',
                     'headers',
                     'header_list',
                     'content',
                     'content_length',
                     'content_url_encoded',
                     'content_json']

        self.tags = set()
        self.whitelisted = False
        self.blacklisted = False

    def __repr__(self):
        return '<WLRequest %s>' % self.request.the_request

    def log_nothing(self, message):
        pass

    def __getattr__(self, key):
        if key in ['uri', 'protocol', 'method', 'host', 'args']:
            setattr(self, key, getattr(self.request, key))
            return getattr(self, key)
        elif key in self.lazy:
            getattr(self, 'lazy_' + str(key))()
            return getattr(self, key)
        else:
            raise AttributeError(key)

    def lazy_parameters(self):
        if self.request.args is not None:
            self.tags.add('wl.has_parameters')
            self.parameters = [arg.split('=', 1)
                               for arg in self.request.args.split('&')]
            for parameter in self.parameters:
                if len(parameter) == 1:
                    parameter.append('')
            self.parameters = sorted(self.parameters,
                                     key=lambda p: p[0])
        else:
            self.parameters = None

    def lazy_parameter_list(self):
        if self.parameters is None:
            self.parameter_list = None
            return
        # parameters already sorted in self.parameter
        self.parameter_list = [p for p, v in self.parameters]

    def lazy_content_length(self):
        if 'Content-Length' in self.request.headers_in:
            self.content_length = \
                int(self.request.headers_in['Content-Length'])
        else:
            self.content_length = 0

    def lazy_content(self):
        if self.content_length == 0:
            self.content = None
            return
        if self.content_length > self.max_content_length:
            self.log('request body length (' +
                     str(self.request.headers_in['Content-Length']) +
                     ' is greater than wlister.max_post_read (' +
                     ' - skipping body analyis')
            self.content = None
            return
        if self.content_length > 0:
            try:
                self.content = self.request.read(self.content_length)
                current_path = os.path.dirname(os.path.abspath(__file__))
                self.request.register_input_filter('wlister_pass_filter',
                                                   'wlister::input_filter',
                                                   current_path)
                self.request.add_input_filter('wlister_pass_filter')
                # Required to forward content when applying input filter
                self.request.body = self.content
            except IOError:
                self.log('reading request body failed' +
                         ' - TimeOut may be reached - ' +
                         'request processing is unknown')
            except Exception as e:
                self.log('Unknown exception occurred - ' + str(e))
        else:
            self.tags.add('wl.bad_content_length')

    def lazy_content_url_encoded(self):
        if 'Content-Type' not in self.request.headers_in:
            self.content_url_encoded = None
            return
        if self.request.headers_in['Content-Type'] != \
                'application/x-www-form-urlencoded':
            self.content_url_encoded = None
            return
        if self.content is None:
            self.content_url_encoded = None
            return
        self.content_url_encoded = \
            [arg.split('=', 1) for arg in self.content.split('&')]
        for p in self.content_url_encoded:
            if len(p) == 1:
                p.append('')
        self.content_url_encoded = sorted(self.content_url_encoded,
                                          key=lambda p: p[0])

    def lazy_content_url_encoded_list(self):
        if self.content_url_encoded is None:
            self.content_url_encoded_list = None
            return
        # posted parameters already sorted in self.content_url_encoded
        self.content_url_encoded_list = \
            [name for name, value in self.content_url_encoded]

    def lazy_headers(self):
        self.headers = []
        for header in sorted(self.request.headers_in):
            values = [value.strip() for value in self.request.headers_in[header].split(',')]
            for value in values:
                self.headers.append([header, value])

    def lazy_header_list(self):
        if self.headers is None:
            self.headers_list = None
            return
        # headers already sorted in self.headers
        self.header_list = [h for h, v in self.headers]

    def lazy_content_json(self):
        if 'Content-Type' not in self.request.headers_in:
            self.content_json = None
            return
        if self.request.headers_in['Content-Type'] != \
                'application/json':
            self.content_json = None
            return
        if self.content is None:
            self.content_json = None
            return
        try:
            self.content_json = json.loads(self.content)
        except:
            self.content_json = None
            self.log('ERROR - can not load JSON content from request - json.loads() failed')

    def lazy_request_id(self):
        import uuid
        u = uuid.uuid4().int
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
        base36 = ''
        while u:
            u, i = divmod(u, 36)
            base36 = alphabet[i] + base36
        self.request_id = base36

    def _log(self):
        request_line = '[' + self.request_id + '] ' + \
            self.method + ' ' + self.uri
        if self.args is not None:
            request_line = request_line + '?' + str(self.args)
        if self.protocol is not None:
            request_line = request_line + ' ' + str(self.protocol)
        self.log(request_line)

        h = self.request.headers_in
        for header in h:
            self.log('[' + self.request_id + '] ' + str(header) +
                     ': ' + str(self.request.headers_in[header]))
        try:
            if self.content_length > 0:
                for chunk in [self.content[i:i+200]
                              for i in range(0, len(self.content), 200)]:
                    self.log('[' + self.request_id + '] ' + str(chunk))
        except Exception as e:
            self.log('can not read HTTP Content from request - ' +
                     str(e))
