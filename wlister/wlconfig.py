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


rules_schema = \
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Conservative json schema defining wlrule format",
    "type": "object",
    "required": ["id"],
    "additionalProperties": False,
    "properties": {
        "id": {
            "type": "string"
        },
        "prerequisite": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "has_tag": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "has_not_tag": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        },
        "match": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "uri": {
                    "type": "string"
                },
                "protocol": {
                    "type": "string"
                },
                "method": {
                    "type": "string"
                },
                "host": {
                    "type": "string"
                },
                "args": {
                    "type": "string"
                },
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "headers": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "content_url_encoded": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "parameters_in": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "headers_in": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "content_url_encoded_in": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "parameters_list": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "headers_list": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "content_url_encoded_list": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "parameters_list_in": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "headers_list_in": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "content_url_encoded_list_in": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "parameters_unique": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "headers_unique": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "content_url_encoded_unique": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "parameters_all_unique": {
                    "type": "string",
                    "enum": ["True", "False"]
                },
                "headers_all_unique": {
                    "type": "string",
                    "enum": ["True", "False"]
                },
                "content_url_encoded_all_unique": {
                    "type": "string",
                    "enum": ["True", "False"]
                },
            }
        },
        "action_if_match": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "whitelist": {
                    "type": "string",
                    "enum": ["True", "False"]
                },
                "set_tag": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "unset_tag": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "action_if_mismatch": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "whitelist": {
                    "type": "string",
                    "enum": ["True", "False"]
                },
                "set_tag": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "unset_tag": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        }
    }
}
