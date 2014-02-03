# -*- coding: utf-8 -*-

from mod_python import apache
import json
from wlrule import WLRule

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
        d = json.load(f)
    except Exception as e:
        log('Rules format is not json compliant - ' +
            str(apache.wl_config['wlister.conf']) +
            str(e))
        return
    for r in d:
        apache.wl_rules.append(WLRule(r, log))


def init_request(request):
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
        request.body_size = int(request.headers_in['Content-Length'])
    else:
        request.body_size = 0

    max_size = apache.wl_config['wlister.max_post_read']
    if request.body_size > max_size:
        log('request body body length is higher than wlister.max_post_read (' +
            max_size + ') - skipping body analyis')
    elif (
        request.body_size > 0 and
        request.body_size < max_size
    ):
        try:
            request.register_input_filter('wlister.pass_filter',
                                          'wlister::input_filter')
            request.add_input_filter('wlister.pass_filter')
            request.body_raw = request.read(request.body_size)
        except IOError:
            log('reading request body failed - TimeOut may be reached - ' +
                'request behavior is unknown')


def init(request):
    init_config(request)
    init_rules()
    init_request(request)


def handler(req):
    init(req)
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
