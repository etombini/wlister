# -*- coding: utf-8 -*-

from mod_python import apache
from wlrule import WLRule

apache.wl_rules = None
apache.wl_config = None

apache.log_error('WLISTER Imported', apache.APLOG_CRIT)

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
                    apache.wl_rules.append(WLRule(r, log))
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
