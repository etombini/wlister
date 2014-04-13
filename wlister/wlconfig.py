# -*- coding: utf-8 -*-

WLCONF = 'wlister.conf'
WLPREFIX = 'wlister.log_prefix'
WLACTION = 'wlister.default_action'
WLMAXPOST = 'wlister.max_post_read'
WLMAXPOST_VALUE = 2048


class WLConfig(object):

    def __init__(self, request, log):
        options = request.get_options()
        self.log = log
        if WLCONF in options:
            self.conf = options[WLCONF]
        else:
            self.conf = None
        if WLPREFIX in options:
            self.prefix = options[WLPREFIX].strip() + ' '
        else:
            self.prefix = ''

        self.default_action = 'block'
        if WLACTION in options:
            if options[WLACTION] in \
                    ['block', 'pass', 'logpass', 'logblock']:
                self.default_action = options[WLACTION]
            else:
                self.log('unknown value for ' + WLACTION +
                         ', set to block')
        else:
            self.log(WLACTION + ' not defined, set to block')
        if WLMAXPOST in options:
            self.max_post_read = options[WLMAXPOST]
        else:
            self.max_post_read = WLMAXPOST_VALUE
            self.log('default request body to be read set to ' +
                     str(WLMAXPOST_VALUE))
