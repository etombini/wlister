# -*- coding: utf-8 -*-

from mod_python import apache
import json
from wlrule import WLRule
from wlrequest import WLRequest

apache.wl_rules = None
apache.wl_config = None

apache.log_error('WLISTER Imported', apache.APLOG_CRIT)


def log(message, log_level=None):
    try:
        apache.log_error(apache.wl_config['wlister.log_prefix'] +
                         ' ' + message, apache.APLOG_CRIT)
    except:
        apache.log_error(message, apache.APLOG_CRIT)


def init_config(request):
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
    options = request.get_options()

    if 'wlister.conf' in options:
        apache.wl_config['wlister.conf'] = options['wlister.conf']

    try:
        apache.wl_config['wlister.log_prefix'] = \
            options['wlister.log_prefix'].strip()
    except:
        apache.wl_config['wlister.log_prefix'] = '[wlister]'

    try:
        if options['wlister.default_action'] in ['block', 'pass', 'learn']:
            apache.wl_config['wlister.default_action'] = \
                options['wlister.default_action']
        else:
            apache.wl_config['wlister.default_action'] = 'block'
            log('unknown value for wlister.default_action ' +
                '(block, pass, learn)')
            log('default action is ' +
                apache.wl_config['wlister.default_action'])
    except:
        apache.wl_config['wlister.default_action'] = 'block'
        log('wlister.default_action not defined')
        log('default action is ' +
            apache.wl_config['wlister.default_action'])

    if 'wlister.max_post_read' in options:
        apache.wl_config['wlister.max_post_read'] = \
            options['wlister.max_post_read']
    else:
        apache.wl_config['wlister.max_post_read'] = 2048
        log('default request body to be read set to ' +
            str(apache.wl_config['wlister.max_post_read']))


def init_rules():
    if apache.wl_rules is not None:
        return
    apache.wl_rules = []
    if 'wlister.conf' not in apache.wl_config:
        log('No configuration file defined - ' +
            'check [PythonOption wlister.conf filename] directive')
        return
    f = None
    try:
        f = open(apache.wl_config['wlister.conf'])
    except:
        log('Can not open configuration file (wlister.conf) - ' +
            str(apache.wl_config['wlister.conf']))
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
            str(apache.wl_config['wlister.conf']) +
            str(e))
        return
    for r in d:
        apache.wl_rules.append(WLRule(r, log))


def handler(req):
    init_config(req)
    init_rules()
    wlrequest = WLRequest(req, log=log)
    log(str(wlrequest))

    for rule in apache.wl_rules:
        rule.analyze(wlrequest)
        if wlrequest.whitelisted:
            return apache.OK
        if wlrequest.blacklisted:
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
    # if there is a body content to forward...
    #if filter.req.body is not None:
    #    filter.write(filter.req.body)
    try:
        filter.write(filter.req.body_raw)
    except AttributeError:
        log('request raw body is not defined')
    finally:
        filter.flush()
        filter.close()
    filter.req.log_error('--------------- END OF FILTER -----------------',
                         apache.APLOG_DEBUG)
