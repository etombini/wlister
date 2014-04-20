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

    def test_content_url_encoded_09(self):
        content = {"var1": "val1", "var2": "val2"}
        r = requests.post('http://localhost/post/', data=content)
        self.assertEqual(r.status_code, 200)

    def test_content_url_encoded_10(self):
        content = {"var2": "val2", "var1": "val1"}
        r = requests.post('http://localhost/post/', data=content)
        self.assertEqual(r.status_code, 200)

    def test_content_url_encoded_11(self):
        content = {"var1": "val1"}
        r = requests.post('http://localhost/post/', data=content)
        self.assertEqual(r.status_code, 404)

    def test_content_url_encoded_12(self):
        content = {"var1": "UnexpectedValue", "var2": "val2"}
        r = requests.post('http://localhost/post/', data=content)
        self.assertEqual(r.status_code, 404)

    def test_content_url_encoded_13(self):
        content = {"var1": "val1", "var2": "val2", "UnexpectedParamter": "whatever"}
        r = requests.post('http://localhost/post/', data=content)
        self.assertEqual(r.status_code, 404)

    def test_content_url_encoded_14(self):
        v = 'val1' * 10000
        content = {"var1": v, "var2": "val2"}
        r = requests.post('http://localhost/post/', data=content)
        self.assertEqual(r.status_code, 404)

    def test_1parameter_15(self):
        r = requests.get('http://localhost/1parameter/?var1=val1&var2')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_list_16(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var2=val2&var3=val3')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_list_17(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var2=val2')
        self.assertEqual(r.status_code, 404)

    def test_parameter_list_18(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var2=val2&var3=val3&val4=val4')
        self.assertEqual(r.status_code, 404)

    def test_parameter_list_19(self):
        r = requests.get('http://localhost/parameter_list/?var1=val1&var2=val2&var3=val3&val3=val4')
        self.assertEqual(r.status_code, 404)
