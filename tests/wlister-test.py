try:
    import unittest2 as unittest
except ImportError:
    import unittest

import requests

class ProxyTest(unittest.TestCase):

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

class AttributeTest(unittest.TestCase):

    def test_whitelisted_uri(self):
        r = requests.get('http://localhost/int/123')
        self.assertEqual(r.status_code, 200, 'match:uri does not work properly')

