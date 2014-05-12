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


class ParametersListInTest(unittest.TestCase):

    def test_parameter_ok(self):
        r = requests.get('http://localhost/parameters_list_in/?var1=AnyValue&var2=AnyValue')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_ok_more_parameter(self):
        r = requests.get('http://localhost/parameters_list_in/?var1=val1&var2=val2&var3=val3')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_ok_duplicated_parameter(self):
        r = requests.get('http://localhost/parameters_list_in/?var1=UnexpectedValue&var2=val2&var1=val1&var3=val3')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameter_ko_less_parameter(self):
        r = requests.get('http://localhost/parameters_list_in/?var1=val1')
        self.assertEqual(r.status_code, 404)

    def test_parameter_ko_wrong_parameter(self):
        r = requests.get('http://localhost/parameters_list_in/?var1=val1&var3=val3')
        self.assertEqual(r.status_code, 404)


class ContentUrlEncodedListInTest(unittest.TestCase):

    def test_content_url_encoded_ok(self):
        content = {"var1": "val1", "var2": "val2"}
        r = requests.post('http://localhost/content_url_encoded_list_in/', data=content)
        self.assertEqual(r.status_code, 200)

    def test_content_url_encoded_ok_more_parameter(self):
        content = {"var1": "val1", "var2": "val2", "var3": "val3"}
        r = requests.post('http://localhost/content_url_encoded_list_in/', data=content)
        self.assertEqual(r.status_code, 200)

    def test_content_url_encoded_ko_wrong_parameter(self):
        content = {"var1": "val1", "var3": "val3", "var4": "var5"}
        r = requests.post('http://localhost/content_url_encoded_list_in/', data=content)
        self.assertEqual(r.status_code, 404)

    def test_content_url_encoded_ko_no_parameter(self):
        content = {}
        r = requests.post('http://localhost/content_url_encoded_list_in/', data=content)
        self.assertEqual(r.status_code, 404)


class HeadersListInTest(unittest.TestCase):

    def test_headers_ok(self):
        h = {"listed_in01": "test", "listed_in02": "test"}
        r = requests.get('http://localhost/headers_list_in/', headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK", "Response is not OK")

    def test_headers_ko_less_header(self):
        h = {"listed_in01": "test"}
        r = requests.get('http://localhost/headers_list_in/', headers=h)
        self.assertEqual(r.status_code, 404)
