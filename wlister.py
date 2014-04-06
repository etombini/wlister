# -*- coding: utf-8 -*-

from mod_python import apache
import json
import syslog

from wlrule import WLRule
from wlrequest import WLRequest
from wlconfig import WLConfig

syslog.openlog('wlister')

apache.wl_rules = None
apache.wl_config = None

apache.log_error('WLISTER Imported', apache.APLOG_CRIT)


def log(message, log_level=None):
    try:
        apache.log_error(apache.wl_config['wlister.log_prefix'] +
                         ' ' + message, apache.APLOG_CRIT)
    except:
        apache.log_error('[wlister] ' + message, apache.APLOG_CRIT)


def _syslog(message):
    syslog.syslog(message)


def init_rules():
    if apache.wl_rules is not None:
        return
    apache.wl_rules = []
    if apache.wl_config.conf == '':
        log('No configuration file defined - ' +
            'check [PythonOption wlister.conf filename] directive')
        return
    f = None
    try:
        f = open(apache.wl_config.conf)
    except:
        log('Can not open configuration file (wlister.conf) - ' +
            str(apache.wl_config.conf))
        return
    d = None
    try:
        j = ''
        for l in f:
            if l[0] == '#':
                continue
            j = j + l
        d = json.loads(j)
    except Exception as e:
        log('Rules format is not json compliant - ' +
            str(apache.wl_config.conf) +
            str(e))
        return
    for r in d:
        apache.wl_rules.append(WLRule(r, log))


def handler(req):
    if apache.wl_config is None:
        apache.wl_config = WLConfig(req, log)
    if apache.wl_rules is None:
        init_rules()
    wlrequest = WLRequest(req, log=log,
                          max_content_length=
                          int(apache.wl_config.max_post_read))
    log(str(wlrequest))

    for rule in apache.wl_rules:
        rule.analyze(wlrequest)
        if wlrequest.whitelisted:
            return apache.OK
        if wlrequest.blacklisted:
            return apache.HTTP_NOT_FOUND

    default_action = apache.wl_config.default_action
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
    # if there is a body content to forward...
    #if filter.req.body is not None:
    #    filter.write(filter.req.body)
    try:
        filter.write(filter.req.body)
        log("REQUEST BODY FOUND " + str(filter.req.body))
    except AttributeError:
        log('request raw body is not defined')
    finally:
        filter.flush()
        filter.close()
    filter.req.log_error('--------------- END OF FILTER -----------------',
                         apache.APLOG_DEBUG)
