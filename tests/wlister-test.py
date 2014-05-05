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


class ParametersListTest(unittest.TestCase):

    def test_parameter_list_ok_same_order(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var2=val2&var3=val3')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_list_ok_different_order(self):
        r = requests.get('http://localhost/parameter_list/?var2=val2&var1=val1&var3=val3')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_list_ko_less_parameter(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var2=val2')
        self.assertEqual(r.status_code, 404)

    def test_parameter_list_ko_more_parameter(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var2=val2&var3=val3&val4=val4')
        self.assertEqual(r.status_code, 404)

    def test_parameter_list_ko_duplicated_parameter(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var2=val2&var3=val3&val3=val4')
        self.assertEqual(r.status_code, 404)

    def test_parameter_list_ko_duplicated_parameters_2(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var1=val1&var2=val2&var3=val3&val3=val4')
        self.assertEqual(r.status_code, 404)



class SimpleTest(unittest.TestCase):

    def test_1parameter_15(self):
        r = requests.get('http://localhost/1parameter/?var1=val1&var2')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_list_16(self):
        r = requests.get('http://localhost/parameter_list/' +
                         '?var1=val1&var2=val2&var3=val3')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_list_16_1(self):
        r = requests.get('http://localhost/parameter_list/' +
                         '?var2=val1&var1=val2&var3=val3')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_list_17(self):
        r = requests.get('http://localhost/parameter_list/' +
                         '?var1=val1&var2=val2')
        self.assertEqual(r.status_code, 404)

    def test_parameter_list_18(self):
        r = requests.get('http://localhost/parameter_list/' +
                         '?var1=val1&var2=val2&var3=val3&val4=val4')
        self.assertEqual(r.status_code, 404)

    def test_parameter_list_19(self):
        r = requests.get('http://localhost/parameter_list/' +
                         '?var1=val1&var2=val2&var3=val3&val3=val4')
        self.assertEqual(r.status_code, 404)

    def test_parameter_list_20(self):
        r = requests.get('http://localhost/parameter_list/' +
                         '?var1=val1&var1=val1&var2=val2&var3=val3&val3=val4')
        self.assertEqual(r.status_code, 404)

