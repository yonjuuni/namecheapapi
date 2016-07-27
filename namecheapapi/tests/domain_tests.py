from nose.tools import raises
from namecheapapi import DomainAPI
from namecheapapi.api.exceptions import NCApiError
from config import (API_USER, API_KEY, USERNAME, CLIENT_IP, SANDBOX, COUPON,
                    DOMAIN)


api = DomainAPI(
    api_user=API_USER,
    api_key=API_KEY,
    username=USERNAME,
    client_ip=CLIENT_IP,
    sandbox=SANDBOX,
    coupon=COUPON
)


def test_domains_check():
    return api.check(DOMAIN)


def test_domains_get_list():
    return api.get_list()


def test_domains_get_tld_list():
    return api.get_tld_list()


def test_domains_get_lock():
    return api.get_lock(DOMAIN)


def test_domains_get_info():
    return api.get_lock(DOMAIN)


@raises(NCApiError)
def test_ncapi_error():
    return api._call('')


def test_domain_get_lock():
    return api.get_lock(DOMAIN)


def test_domain_set_lock():
    return api.set_lock(DOMAIN, lock=True)


def test_domain_get_nameservers():
    return api.get_nameservers(DOMAIN)


def test_domain_set_nameservers():
    return api.set_nameservers(DOMAIN, nameservers=['ns1.domainname.com',
                                                    'ns2.domainname.com'])


def test_domain_set_default_nameservers():
    return api.set_nameservers(DOMAIN, set_default=True)
