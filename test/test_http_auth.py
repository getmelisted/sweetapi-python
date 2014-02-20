from lib import http_auth, config

__author__ = 'pat'

import unittest


class MockRequest:
    def __init__(self):
        self.values = {}


class HttpAuthTestCase(unittest.TestCase):
    def test_auth_with_api_key(self):
        self.assertEqual(http_auth.is_valid_api_key(config.local_api_key), True)

    def test_authenticate(self):
        self.assertIsNotNone(http_auth.authenticate())

    def test_extract_api_key_from_request(self):
        req = MockRequest()
        req.values['api_key'] = 'a_key'
        self.assertIsNotNone(http_auth.extract_api_key_from_request(req))
        self.assertEqual('a_key', http_auth.extract_api_key_from_request(req))


if __name__ == '__main__':
    unittest.main()
