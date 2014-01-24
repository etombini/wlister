try:
    import unittest2 as unittest
except ImportError:
    import unittest

import requests


class SimpleTest(unittest.TestCase):

    def test_flask_ok(self):
        r = requests.get('http://localhost:5000')
        self.assertEqual(r.status_code, 200)

    def test_proxy_ok(self):
        r = requests.get('http://localhost/')
        self.assertEqual(r.status_code, 200)

    def test_01(self):
        r = requests.get('http://localhost/abc')
        self.assertEqual(r.status_code, 404)

    def test_02(self):
        r = requests.get('http://localhost/int/123')
        self.assertEqual(r.status_code, 200)
