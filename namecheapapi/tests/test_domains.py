import unittest
from namecheapapi import DomainAPI
from namecheapapi.api.exceptions import NCApiError
from namecheapapi.tests.config import (API_USER, API_KEY, USERNAME,
                                       CLIENT_IP, SANDBOX, COUPON, DOMAIN)


class NcAPITest(unittest.TestCase):

    # TODO add get_contacts, set_contacts

    def setUp(self):
        self.api = DomainAPI(
            api_user=API_USER,
            api_key=API_KEY,
            username=USERNAME,
            client_ip=CLIENT_IP,
            sandbox=SANDBOX,
            coupon=COUPON
        )

    def test_ncapi_error(self):
        with self.assertRaises(NCApiError):
            self.api._call('')

    def test_domains_check(self):
        response = self.api.check(DOMAIN)
        self.assertIsInstance(response, dict)
        self.assertIn(DOMAIN, response)

    def test_domains_get_list(self):
        response = self.api.get_list()
        self.assertIsInstance(response, list)

    def test_domains_get_tld_list(self):
        response = self.api.get_tld_list()
        self.assertIsInstance(response, dict)

    def test_domains_get_lock(self):
        response = self.api.get_lock(DOMAIN)
        self.assertIsInstance(response, bool)

    def test_domains_set_lock(self):
        response = self.api.set_lock(DOMAIN, lock=True)
        self.assertIsInstance(response, bool)

    def test_domains_get_info(self):
        response = self.api.get_info(DOMAIN)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('Domain'), DOMAIN)

    def test_domains_get_nameservers(self):
        response = self.api.get_nameservers(DOMAIN)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('Domain'), DOMAIN)

    def test_domains_set_nameservers(self):
        response = self.api.set_nameservers(
            DOMAIN, nameservers=['ns1.domainname.com', 'ns2.domainname.com'])
        self.assertIsInstance(response, bool)

    def test_domains_set_default_nameservers(self):
        response = self.api.set_nameservers(DOMAIN, set_default=True)
        self.assertIsInstance(response, bool)


if __name__ == '__main__':
    unittest.main()
