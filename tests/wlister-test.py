try:
    import unittest2 as unittest
except ImportError:
    import unittest

import requests


class SimpleTest(unittest.TestCase):

    def test_flask_ok(self):
        r = requests.get('http://localhost:5000')
        self.assertEqual(r.status_code, 200)

    def test_pass(self):
        self.assertEqual(10, 7 + 3)

    def test_fail(self):
        self.assertEqual(10, 7 + 3)
