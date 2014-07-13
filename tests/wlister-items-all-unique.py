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


class ParametersAllUniqueTest(unittest.TestCase):

    def test_parameters_ok(self):
        r = requests.get('http://localhost/parameters_all_unique/?var1=val1&var2=val2&var3=val2')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameters_ok_different_order(self):
        r = requests.get('http://localhost/parameters_all_unique/?var2=val2&var1=val1&var3=sdsfsdfsdf')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

    def test_parameters_ko_duplicate01(self):
        r = requests.get('http://localhost/parameters_all_unique/?var1=ValueNotExpected&var2=val2&var1=val76543')
        self.assertEqual(r.status_code, 404)

    def test_parameters_ko_duplicate02(self):
        r = requests.get('http://localhost/parameters_all_unique/?var2=val2&var1=val1&var1=val3')
        self.assertEqual(r.status_code, 404)

    def test_parameters_ok_less_parameter(self):
        r = requests.get('http://localhost/parameters_all_unique/?var1=val1')
        self.assertEqual(r.status_code, 200)

    def test_parameters_ok_more_parameter(self):
        r = requests.get('http://localhost/parameters_all_unique/?var1=val1&v=v&a=a@r=z')
        self.assertEqual(r.status_code, 200)


class ContentUrlEncodedAllUniqueTest(unittest.TestCase):

    def test_content_url_encoded_ko_no_content(self):
        r = requests.get('http://localhost/content_url_encoded_all_unique/?var1=val1&var2=val2&var3=val2')
        self.assertEqual(r.status_code, 404)

    def test_content_url_encoded_ok_same_order(self):
        content = {"var1": "val1", "var2": "val2"}
        r = requests.post('http://localhost/content_url_encoded_all_unique/', data=content)
        self.assertEqual(r.status_code, 200)

    def test_content_url_encoded_ok_more_parameter(self):
        content = {"var2": "val2", "var1": "val1", "var3": "val1"}
        r = requests.post('http://localhost/content_url_encoded_all_unique/', data=content)
        self.assertEqual(r.status_code, 200)

    def test_content_url_encoded_ok_less_parameter(self):
        content = {"var1": "val1"}
        r = requests.post('http://localhost/content_url_encoded_all_unique/', data=content)
        self.assertEqual(r.status_code, 200)

    def test_content_url_encoded_ko_duplicate_parameter01(self):
        import telnetlib
        t = telnetlib.Telnet('localhost', 80)
        t.write('GET /content_url_encoded_all_unique/ HTTP/1/1\n')
        t.write('Host: localhost\n')
        t.write('header-test: test\n')
        t.write('header-duplicated01: test\n')
        t.write('Accept: */*\n')
        t.write('Content-Type: application/x-www-form-urlencoded\n')
        t.write('Content-Length: 0\n')
        t.write('User-Agent: python-requests/2.2.0 CPython/2.7.3 Linux/3.8.0-29-generic\n\n')
        r = t.read_all()
        t.close()
        self.assertEqual(int(r[9:12]), 404)

    def test_content_url_encoded_ko_duplicate_parameter02(self):
        import telnetlib
        t = telnetlib.Telnet('localhost', 80)
        t.write('GET /content_url_encoded_all_unique/ HTTP/1/1\n')
        t.write('Host: localhost\n')
        t.write('Accept: */*\n')
        t.write('Content-Type: application/x-www-form-urlencoded\n')
        t.write('Content-Length: 29\n')
        t.write('User-Agent: python-requests/2.2.0 CPython/2.7.3 Linux/3.8.0-29-generic\n\n')
        t.write('var1=val1&var2=val2&var1=val1\n\n')
        r = t.read_all()
        t.close()
        self.assertEqual(int(r[9:12]), 404)


class HeadersAllUniqueTest(unittest.TestCase):

    def test_headers_ok(self):
        import telnetlib
        t = telnetlib.Telnet('localhost', 80)
        t.write('GET /headers_all_unique/ HTTP/1/1\n')
        t.write('Host: localhost\n')
        t.write('header-test: test\n')
        t.write('header-duplicated01: test\n')
        t.write('Accept: */*\n')
        t.write('User-Agent: python-requests/2.2.0 CPython/2.7.3 Linux/3.8.0-29-generic\n\n')
        r = t.read_all()
        t.close()
        self.assertEqual(int(r[9:12]), 200)

    def test_headers_ko_separated_value(self):
        h = {'header-test': 'UnexpectedValue, value separated', 'header-similar': 'xxx'}
        r = requests.get('http://localhost/headers_all_unique/', headers=h)
        self.assertEqual(r.status_code, 404)

    def test_headers_ko_case_insensitive_header01(self):
        import telnetlib
        t = telnetlib.Telnet('localhost', 80)
        t.write('GET /headers_all_unique/ HTTP/1/1\n')
        t.write('Host: localhost\n')
        t.write('header-test: test\n')
        t.write('Header-Test: test\n')
        t.write('header-duplicated01: test\n')
        t.write('Accept: */*\n')
        t.write('User-Agent: python-requests/2.2.0 CPython/2.7.3 Linux/3.8.0-29-generic\n\n')
        r = t.read_all()
        t.close()
        self.assertEqual(int(r[9:12]), 404)

    def test_headers_ko_duplicated_header01(self):
        import telnetlib
        t = telnetlib.Telnet('localhost', 80)
        t.write('GET /headers_all_unique/ HTTP/1/1\n')
        t.write('Host: localhost\n')
        t.write('header-test: test\n')
        t.write('header-duplicated01: test\n')
        t.write('Accept: */*\n')
        t.write('User-Agent: python-requests/2.2.0 CPython/2.7.3 Linux/3.8.0-29-generic\n')
        t.write('Accept-Encoding: gzip, deflate, compress\n')
        t.write('Accept-Encoding: banana, orange, lemon\n')
        t.write('header-test: test-duplicate\n\n')
        r = t.read_all()
        t.close()
        self.assertEqual(int(r[9:12]), 404)

    def test_headers_ko_duplicated_header02(self):
        import telnetlib
        t = telnetlib.Telnet('wlister.vm', 80)
        t.write('GET /headers_all_unique/ HTTP/1/1\n')
        t.write('Host: localhost\n')
        # t.write('Accept: */*\n')
        t.write('User-Agent: python-requests/2.2.0 CPython/2.7.3 Linux/3.8.0-29-generic\n')
        t.write('Accept-Encoding: gzip, deflate, compress\n')
        t.write('header-test: test\n')
        t.write('header-duplicated02: test\n')
        t.write('header-test: test\n')
        t.write('header-test: test01\n')
        t.write('header-test: test02\n')
        t.write('header-test: test03\n')
        t.write('header-test: test04\n\n')
        r = t.read_all()
        t.close()
        self.assertEqual(int(r[9:12]), 404)

    def test_headers_ko_missing_header(self):
        import telnetlib
        t = telnetlib.Telnet('wlister.vm', 80)
        t.write('GET /headers_all_unique/ HTTP/1/1\n')
        t.write('Host: localhost\n')
        t.write('Accept: */*\n')
        t.write('Supernumerary: ouh yeah\n')
        t.write('User-Agent: python-requests/2.2.0 CPython/2.7.3 Linux/3.8.0-29-generic\n')
        t.write('Accept-Encoding: gzip, deflate, compress\n\n')
        r = t.read_all()
        t.close()
        self.assertEqual(int(r[9:12]), 404)
