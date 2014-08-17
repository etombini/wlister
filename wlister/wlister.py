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


from mod_python import apache

import json
import syslog
import jsonschema

from wlrule import WLRule
from wlrequest import WLRequest
import wlconfig


apache.wl_rules = None
apache.wl_config = None

apache.log_error('WLISTER Imported', apache.APLOG_CRIT)


# def log(message, log_level=None):
#     try:
#         apache.log_error(apache.wl_config['wlister.log_prefix'] +
#                          ' ' + message, apache.APLOG_CRIT)
#     except:
#         apache.log_error('[wlister] ' + message, apache.APLOG_CRIT)


syslog.openlog('wlister')


def _syslog(message):
    syslog.syslog(message)


def init_rules():
    if apache.wl_rules is not None:
        return
    apache.wl_rules = []
    if apache.wl_config.conf == '':
        _syslog('No configuration file defined - ' +
                'check [PythonOption wlister.conf filename] directive')
        return
    f = None
    try:
        f = open(apache.wl_config.conf)
    except:
        _syslog('Can not open configuration file (wlister.conf) - ' +
                str(apache.wl_config.conf))
        return
    d = None
    try:
        j = ''
        for l in f:
            if l[0] == '#':
                j = j + '\n'
            else:
                j = j + l
        d = json.loads(j)
    except Exception as e:
        _syslog('Rules format is not json compliant - ' +
                str(apache.wl_config.conf) + ' - ' +
                str(e))
        return
    try:
        for r in d:
            jsonschema.validate(r, wlconfig.rules_schema)
    except Exception as e:
        _syslog('ERROR - Rules format is not compliant - ' +
                str(apache.wl_config.conf) + ' - ' +
                str(e))
        return
    for r in d:
        apache.wl_rules.append(WLRule(r, _syslog))


def handler(req):
    if apache.wl_config is None:
        apache.wl_config = wlconfig.WLConfig(req, _syslog)
    if apache.wl_rules is None:
        init_rules()
    wlrequest = WLRequest(req, log=_syslog,
                          max_content_length=int(apache.wl_config.max_post_read))

    for rule in apache.wl_rules:
        rule.analyze(wlrequest)
        if wlrequest.whitelisted:
            return apache.OK
        if wlrequest.blacklisted:
            return apache.HTTP_NOT_FOUND

    if apache.wl_config.default_action[:3] == 'log':
        wlrequest._log()
    if apache.wl_config.default_action[-5:] == 'block':
        return apache.HTTP_NOT_FOUND
    if apache.wl_config.default_action[-4:] == 'pass':
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
    # if there is a body content to forward...
    # if filter.req.body is not None:
    #    filter.write(filter.req.body)
    try:
        filter.write(filter.req.body)
        _syslog("REQUEST BODY FOUND " + str(filter.req.body))
    except AttributeError:
        _syslog('request raw body is not defined')
    finally:
        filter.flush()
        filter.close()
    filter.req.log_error('--------------- END OF FILTER -----------------',
                         apache.APLOG_DEBUG)
