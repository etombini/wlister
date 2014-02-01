try:
    import unittest2 as unittest
except ImportError:
    import unittest

import requests


class SimpleTest(unittest.TestCase):

    def test_flask_ok(self):
        r = requests.get('http://localhost:5000')
        self.assertEqual(r.status_code, 200,
                         'HTTP target service is not running')

    def test_proxy_ok(self):
        r = requests.get('http://localhost/')
        self.assertEqual(r.status_code, 200,
                         'Proxy service is not running properly')

    def test_dummy_uri(self):
        r = requests.get('http://localhost/abc')
        self.assertEqual(r.status_code, 404,
                         'Filtering service not working')

    def test_whitelisted_uri(self):
        r = requests.get('http://localhost/int/123')
        self.assertEqual(r.status_code, 200)

    # parameters testing (all parameters must match)
    # Rule definition
    #{
    #    "match": {
    #        "url": "^/parameters$",
    #        "parameters": [
    #            ["var1", "^val1$"],
    #            ["var2", "^val2$"]
    #            ]
    #    },
    #    "action_if_match": {
    #        "whitelist": "True"
    #    }
    #}
    def test_parameters_03(self):
        r = requests.get('http://localhost/parameters?var1=val1&var2=val2')
        self.assertEqual(r.status_code, 200)

    def test_parameters_04(self):
        r = requests.get('http://localhost/parameters?var2=val2&var1=val1')
        self.assertEqual(r.status_code, 200)

    def test_parameters_05(self):
        r = requests.get('http://localhost/parameters?var2=val2&var1=val1')
        self.assertEqual(r.status_code, 200)

    def test_parameters_06(self):
        r = requests.get('http://localhost/parameters?var2=val2')
        self.assertEqual(r.status_code, 404)

    def test_parameters_07(self):
        r = requests.get('http://localhost/parameters?var1=ValueNotExpected&var2=val2')
        self.assertEqual(r.status_code, 404)

    def test_parameters_08(self):
        r = requests.get('http://localhost/parameters?var1=val1&var2=val2&UnexpectedParameter=whatever')
        self.assertEqual(r.status_code, 404)
