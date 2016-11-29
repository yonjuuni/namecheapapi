import collections
import typing
from datetime import datetime
from datetime import timedelta
from math import ceil
from xml.etree.ElementTree import fromstring
from .session import Session
from .commands import *

ADDRESS_TYPES = ['Registrant', 'Tech', 'Admin', 'AuxBilling']
REQUIRED_ADDRESS_PARAMS = [
    'FirstName', 'LastName', 'Address1', 'City', 'StateProvince',
    'PostalCode', 'Country', 'Phone', 'EmailAddress'
]
OPTIONAL_ADDRESS_PARAMS = [
    'OrganizationName', 'JobTitle', 'Address2', 'StateProvinceChoice',
    'PhoneExt', 'Fax'
]


class DomainAPI(Session):

    def register(self, domain: str, years: int = 1, address: dict = {},
                 nameservers: typing.Union[list, set, tuple] = None,
                 coupon: str = None, add_whoisguard: bool = True,
                 enable_whoisguard: bool = True) -> dict:
        """Register a domain name.

        https://www.namecheap.com/support/api/methods/domains/create.aspx

        NOTE: this method will charge your Namecheap account!

        Arguments:
            domain -- domain name to register
            years -- years to register the domain for
            address -- a dict with the address values.

                REQUIRED address dict keys:
                    'FirstName', 'LastName', 'Address1', 'City',
                    'StateProvince', 'PostalCode', 'Country', 'Phone',
                    'EmailAddress'
                OPTIONAL address dict keys:
                    'OrganizationName', 'JobTitle', 'Address2',
                    'StateProvinceChoice', 'PhoneExt', 'Fax'

                Please refer to Namecheap's API docs for help on how
                each field should be formatted.

                example_address = {
                    'FirstName': 'Peter',
                    'LastName': 'Griffin',
                    'Address1': '31 Spooner St.',
                    'City': 'Quahog',
                    'StateProvince': 'RI',
                    'PostalCode': '00093',
                    'Country': 'US',
                    'Phone': '+1.123456789',
                    'EmailAddress': 'peter@griffin.tv'
                }

            nameservers -- list/set/tuple with nameservers (str)
            coupon -- optional coupon code
            add_whoisguard -- indicate whether you want to add a free
                WhoisGuard with your domain (only applies to eligible
                domains)
            enable_whoisguard -- indicate whether you want to enable
                free WhoisGuard
        """

        # Create a bigass query
        query = {
            'DomainName': domain,
            'Years': years,
            'AddFreeWhoisGuard': add_whoisguard,
            'WGEnabled': enable_whoisguard,
        }

        # Optional query parameters
        if coupon:
            query['PromotionCode'] = coupon
        elif self.coupon:
            query['PromotionCode'] = self.coupon

        if nameservers:
            query['Nameservers'] = ','.join(nameservers)

        address = self._build_address_dict(address)

        query = {**query, **address}

        xml = self._call(DOMAINS_REGISTER, query, post=True).find(
            self._tag('DomainCreateResult'))

        return {
            'Domain': xml.get('Domain'),
            'Success': xml.get('Registered').lower() == 'true',
            'ChargedAmount': float(xml.get('ChargedAmount')),
            'ID': int(xml.get('DomainID')),
            'OrderID': int(xml.get('OrderID')),
            'TransactionID': int(xml.get('TransactionID')),
            'WhoisGuardEnabled': xml.get('WhoisguardEnable').lower() == 'true',
            'NonRealTimeDomain': xml.get('NonRealTimeDomain').lower() == 'true'
        }

    def renew(self, domain: str, years: int = 1, coupon: str = None,
              check_status_first: bool = False) -> dict:
        """Domain renewal option.

        https://www.namecheap.com/support/api/methods/domains/renew.aspx

        NOTE: this method will charge your Namecheap account!

        ***Premium Domain renewals are not supported at this time***

        Arguments:
            domain -- domain name
            years -- renewal years (default: 1)
            coupon -- coupon code. If provided, overrides the
                session-specified coupon.
            check_status_first* -- if set to True, get_info() will be
                called first to check if the domain is expired. If it
                is, reactivate() will be called instead.

        Returns:
            A dict with order-related information.

        *check_status_first is experimental, use with caution.
        """
        if coupon:
            query['PromotionCode'] = coupon
        elif self.coupon:
            coupon = self.coupon
            query['PromotionCode'] = coupon

        if check_status_first:
            self._get_gmt_offset()
            domain_info = self.get_info(domain)
            if (domain_info['Expiration'] - timedelta(hours=self.gmt_offset) <
                    datetime.utcnow()):
                return self.reactivate(domain, coupon=coupon)

        query = {'DomainName': domain, 'Years': years}

        xml = self._call(DOMAINS_RENEW, query).find(
            self._tag('DomainRenewResult'))

        return {
            'Domain': xml.get('DomainName'),
            'ID': int(xml.get('DomainID')),
            'Success': xml.get('Renew').lower() == 'true',
            'OrderID': int(xml.get('OrderID')),
            'TransactionID': int(xml.get('TransactionID')),
            'ChargedAmount': float(xml.get('ChargedAmount')),
            'Expiration':
                datetime.strptime(xml.find(
                    self._tag('DomainDetails')).find(
                    self._tag('ExpiredDate')).text, '%m/%d/%Y %I:%M:%S %p')
        }

    def reactivate(self, domain: str, years: int = 1,
                   coupon: str = None) -> dict:
        """Reactivate the domain.

        https://www.namecheap.com/support/api/methods/domains/reactivate.aspx

        NOTE: this method will charge your Namecheap account! Also, even
            though years is a modifiable argument, it's advisable to
            leave it at a minimal value (e.g. 1 year), as trying to add
            more years may result in an error.

        ***Premium Domains reactivation is not supported at this time***

        Arguments:
            domain -- domain name
            years -- renewal years (default: 1)
            coupon -- coupon code. If provided, overrides the
                session-specified coupon.

        Returns:
            A dict with order-related information.
        """
        query = {'DomainName': domain, 'YearsToAdd': years}

        if coupon:
            query['PromotionCode'] = coupon
        elif self.coupon:
            query['PromotionCode'] = self.coupon

        xml = self._call(DOMAINS_REACTIVATE, query).find(
            self._tag('DomainReactivateResult'))

        return {
            'Domain': xml.get('Domain'),
            'Success': xml.get('IsSuccess').lower() == 'true',
            'OrderID': int(xml.get('OrderID')),
            'TransactionID': int(xml.get('TransactionID')),
            'ChargedAmount': float(xml.get('ChargedAmount')),
        }

    def get_info(self, domain: str) -> dict:
        """Get domain information.

        https://www.namecheap.com/support/api/methods/domains/get-info.aspx

        Domain must be listed in your Namecheap account.

        Arguments:
            domain -- domain name (e.g. 'google.com')

        Returns:
            Dict with domain information
        """
        xml = self._call(DOMAINS_GET_INFO, {'DomainName': domain}).find(
            self._tag('DomainGetInfoResult'))

        # Basic information
        result = {
            'Domain': xml.get('DomainName'),
            'Owner': xml.get('OwnerName'),
            'Status': xml.get('Status'),
            'ID': xml.get('ID'),
            'IsOwner': xml.get('IsOwner').lower() == 'true',
            'Full modification rights':
                xml.find(self._tag('Modificationrights')).
                get('All').lower() == 'true'
        }

        result['Creation'] = datetime.strptime(xml.find(
            self._tag('DomainDetails')).find(self._tag('CreatedDate')).text,
            '%m/%d/%Y')
        result['Expiration'] = datetime.strptime(xml.find(
            self._tag('DomainDetails')).find(self._tag('ExpiredDate')).text,
            '%m/%d/%Y')

        # WhoisGuard details
        wg = xml.find(self._tag('Whoisguard'))
        result['WhoisGuard'] = {
            'Enabled': wg.get('Enabled').lower() == 'true',
            'Expiration':
                datetime.strptime(wg.find(self._tag('ExpiredDate')).text,
                                  '%m/%d/%Y'),
            'ID': wg.find(self._tag('ID')).text,
            'Email':
                wg.find(self._tag('EmailDetails')).get('WhoisGuardEmail'),
            'Forwarded to':
                wg.find(self._tag('EmailDetails')).get('ForwardedTo'),
            'Last email auto-change date':
                wg.find(self._tag('EmailDetails')).get(
                'LastAutoEmailChangeDate') or None,
            'Email auto-change frequency':
                wg.find(self._tag('EmailDetails')).get(
                    'AutoEmailChangeFrequencyDays')
        }

        # Premium DNS details
        pdns = xml.find(self._tag('PremiumDnsSubscription'))

        result['PremiumDNS'] = {
            'Creation': pdns.find(self._tag('CreatedDate')).text,
            'Expiration': pdns.find(self._tag('ExpirationDate')).text,
            'ID': pdns.find(self._tag('SubscriptionId')).text,
            'Auto-renew': pdns.find(
                self._tag('UseAutoRenew')).text.lower() == 'true',
            'Active': pdns.find(self._tag('IsActive')).text.lower() == 'true'
        }

        # DNS details
        dns = xml.find(self._tag('DnsDetails'))
        result['DNS'] = {
            'Type': dns.get('ProviderType'),
            'Using NC DNS': dns.get('IsUsingOurDNS').lower() == 'true',
            'Host records count': dns.get('HostCount'),
            'Email type': dns.get('EmailType'),
            'Dynamic DNS': dns.get('DynamicDNSStatus').lower() == 'true',
            'Failover DNS': dns.get('IsFailover').lower() == 'true',
            'Nameservers': [ns.text for ns in
                            dns.findall(self._tag('Nameserver'))]
        }

        return result

    def get_list(self, _type: str = 'ALL',
                 search_term: str = None) -> typing.List[dict]:
        """Get the list of domains.

        https://www.namecheap.com/support/api/methods/domains/get-list.aspx

        Arguments:
            _type -- possible values: 'ALL', 'EXPIRING', 'EXPIRED'
            search_term -- keyword to look for in the domain list.

        Returns:
            A list containing dicts with domain information.
        """
        domains = []

        # A check on the total domain number (minimal PageSize is 10)
        query = {'ListType': _type, 'PageSize': 10}
        if search_term:
            query['SearchTerm'] = search_term

        xml = self._call(DOMAINS_GET_LIST, query).find(self._tag('Paging'))
        total_domains = int(xml.find(self._tag('TotalItems')).text)

        # A call is sent for every 100-item page
        # TODO: check performance on big accounts
        for page in range(1, ceil(total_domains / 100) + 1):

            query = {
                'ListType': _type,
                'Page': page,
                'PageSize': 100
            }
            if search_term:
                query['SearchTerm'] = search_term

            xml = self._call(
                DOMAINS_GET_LIST, query).find(self._tag('DomainGetListResult'))

            for domain in xml.findall(self._tag('Domain')):
                domains.append({
                    'Domain': domain.get('Name'),
                    'ID': domain.get('ID'),
                    'Owner': domain.get('User'),
                    'Creation': datetime.strptime(domain.get('Created'),
                                                  '%m/%d/%Y'),
                    'Expiration': datetime.strptime(domain.get('Expires'),
                                                    '%m/%d/%Y'),
                    'WhoisGuard': domain.get('WhoisGuard'),
                    'Expired': domain.get('IsExpired').lower() == 'true',
                    'Locked': domain.get('IsLocked').lower() == 'true',
                    'Auto-renew': domain.get('AutoRenew').lower() == 'true',
                })

        return domains

    def get_tld_list(self) -> typing.Dict[str, dict]:
        """Get TLD list

        https://www.namecheap.com/support/api/methods/domains/get-tld-list.aspx

        NOTE: Namecheap strongly recommend that you cache this API
        response to avoid repeated calls.

        Arguments:
            None

        Returns:
            A dict:
            {'tld': {details...},
             'tld2': {details...}
            }
        """
        xml = self._call(DOMAINS_GET_TLD_LIST).find(self._tag('Tlds'))

        result = {}

        for tld in xml.findall(self._tag('Tld')):
            tld_name = tld.get('Name')
            result[tld_name] = tld.attrib
            result[tld_name]['Description'] = tld.text
            del result[tld_name]['Name']

            # Normalize dict values
            for key in result[tld_name]:
                if result[tld_name][key].lower() == 'false':
                    result[tld_name][key] = False
                elif result[tld_name][key].lower() == 'true':
                    result[tld_name][key] = True
                elif result[tld_name][key].lower() == '':
                    result[tld_name][key] = None
                else:
                    try:
                        int(result[tld_name][key])
                    except ValueError:
                        continue
                    else:
                        result[tld_name][key] = int(result[tld_name][key])

        return result

    def check(self, domains: typing.Union[str, list, tuple,
              set]) -> typing.Dict[str, bool]:
        """Check domain availability.

        https://www.namecheap.com/support/api/methods/domains/check.aspx

        Arguments:
            domains -- any iterable (str for single domain; list, set,
                tuple for multiple domains)

        Returns:
            Dict with boolean values for domain availability.
            E.g.:
                {'google.com': False,
                 'yourawesomedomain.name': True}

        """
        if isinstance(domains, str):
            domains = [domains, ]
        xml = self._call(DOMAINS_CHECK, {'DomainList': ','.join(domains)})

        result = {}
        for item in xml.findall(self._tag('DomainCheckResult')):
            result[item.get('Domain')] = (
                item.get('Available').lower() == 'true')

        return result

    def get_contacts(self, domain: str) -> dict:
        """Obtain contact details for a domain.

        https://www.namecheap.com/support/api/methods/domains/get-contacts.aspx

        Arguments:
            domain -- domain name

        Returns:
            A dict with contact details:

            {'Registrant': {'Address1': '31 Spooner St.',
                       'City': 'Quahog',
                       'Country': 'US',
                       'EmailAddress': 'peter@griffin.tv',
                       'FirstName': 'Peter',
                       'LastName': 'Griffin',
                       ....},
            'Admin': {'Address1': '31 Spooner St.',
                      'City': 'Quahog',
                      'Country': 'US',
                      'EmailAddress': 'peter@griffin.tv',
                      'FirstName': 'Peter',
                      'LastName': 'Griffin',
                       ........},
            ......}

        """
        xml = self._call(DOMAINS_GET_CONTACTS, {'DomainName': domain}).find(
            self._tag('DomainContactsResult'))

        result = {}

        for _type in ADDRESS_TYPES:
            type_xml = xml.find(self._tag(_type))
            result[_type] = {
                'ReadOnly': type_xml.get('ReadOnly').lower() == 'true'}
            for field in REQUIRED_ADDRESS_PARAMS + OPTIONAL_ADDRESS_PARAMS:
                field_xml = type_xml.find(self._tag(field))
                if field_xml.text:
                    result[_type][field] = field_xml.text

        return result

    def set_contacts(self, domain: str, address: dict) -> bool:
        """Set contact information for your domain

        https://www.namecheap.com/support/api/methods/domains/set-contacts.aspx

        Arguments:
            domain -- domain name
            address -- a dict with the address values.

                REQUIRED address dict keys:
                    'FirstName', 'LastName', 'Address1', 'City',
                    'StateProvince', 'PostalCode', 'Country', 'Phone',
                    'EmailAddress'
                OPTIONAL address dict keys:
                    'OrganizationName', 'JobTitle', 'Address2',
                    'StateProvinceChoice', 'PhoneExt', 'Fax'

                Please refer to Namecheap's API docs for help on how
                each field should be formatted.

                example_address = {
                    'FirstName': 'Peter',
                    'LastName': 'Griffin',
                    'Address1': '31 Spooner St.',
                    'City': 'Quahog',
                    'StateProvince': 'RI',
                    'PostalCode': '00093',
                    'Country': 'US',
                    'Phone': '+1.123456789',
                    'EmailAddress': 'peter@griffin.tv'
                }
        Returns:
            boolean value indicating success/failure of the operation
        """

        address = self._build_address_dict(address)
        query = {'DomainName': domain, **address}

        xml = self._call(DOMAINS_SET_CONTACTS, query, post=True).find(
            self._tag('DomainSetContactResult'))

        return xml.get('IsSuccess').lower() == 'true'

    def get_lock(self, domain: str, verbose: bool = False) -> bool:
        """Get registrar lock status

        https://www.namecheap.com/support/api/methods/domains/get-registrar-lock.aspx

        Arguments:
            domain -- domain name
            verbose -- (bool) set to True if you want to get detailed
                lock info (see Returns section below).

        Returns:
            A boolean value representing the lock status.

            Use verbose=True if you want to get the detailed info that
                includes ClientUpdateProhibited, ClientDeleteProhibited
                and ClientHold statuses.
        """
        xml = self._call(DOMAINS_GET_LOCK, {
            'DomainName': domain
        }).find(self._tag('DomainGetRegistrarLockResult'))

        if not verbose:
            return xml.get('RegistrarLockStatus').lower() == 'true'

        return {
            'Domain': xml.get('Domain'),
            'RegistrarLock':
                xml.get('RegistrarLockStatus').lower() == 'true',
            'ClientUpdateProhibited':
                xml.get('IsClientUpdateProhibited').lower() == 'true',
            'ClientDeleteProhibited':
                xml.get('IsClientDeleteProhibited').lower() == 'true',
            'ClientHold':
                xml.get('IsClientHold').lower() == 'true'
        }

    def set_lock(self, domain: str, lock: bool = True) -> bool:
        """Set registrar lock

        https://www.namecheap.com/support/api/methods/domains/set-registrar-lock.aspx

        Arguments:
            domain -- domain name
            lock -- lock (True/False)

        Returns:
            True if lock status was successfully updated, False
                otherwise
        """
        query = {
            'DomainName': domain,
            'LockAction': 'LOCK' if lock else 'UNLOCK'
        }

        xml = self._call(DOMAINS_SET_LOCK, query).find(
            self._tag('DomainSetRegistrarLockResult'))

        return xml.get('IsSuccess').lower() == 'true'

    def create_nameserver(self):
        pass

    def delete_nameserver(self):
        pass

    def update_nameserver(self):
        pass

    def get_nameserver_info(self):
        pass

    def set_nameservers(self, domain: typing.Sequence,
                        nameservers: typing.Iterable = None,
                        set_default: bool = False) -> bool:
        """Set nameservers for a domain name.

        https://www.namecheap.com/support/api/methods/domains-dns/set-default.aspx
        https://www.namecheap.com/support/api/methods/domains-dns/set-custom.aspx

        Arguments:
            domain -- domain name. Can be a string ('domain.tld') or a
                list/tuple of two elements: ('domain', 'tld').
            nameservers -- iterable with nameserver strings. In most
                cases you should provide from 2 to 12 nameservers, some
                TLDs do have different max number, though.
            set_default -- setting to True will set Namecheap DNS

        Returns:
            bool value with update status.
        """
        host_name, tld = self._normalize_domain(domain)

        if set_default:
            xml = self._call(
                DOMAINS_SET_DEFAULT_NS, {'SLD': host_name, 'TLD': tld}).find(
                self._tag('DomainDNSSetDefaultResult'))

        else:
            query = {
                'SLD': host_name,
                'TLD': tld,
                'Nameservers': ','.join(nameservers)
            }
            xml = self._call(
                DOMAINS_SET_CUSTOM_NS, query).find(
                self._tag('DomainDNSSetCustomResult'))

        return xml.get('Updated').lower() == 'true'

    def get_nameservers(self, domain: typing.Sequence) -> dict:
        """Get list of nameservers

        https://www.namecheap.com/support/api/methods/domains-dns/get-list.aspx

        Arguments:
            domain -- domain name. Can be a string ('domain.tld') or a
                list/tuple of two elements: ('domain', 'tld').

        Returns:
            A dict with domain nameserver information
            {'Domain': domain,
             'Namecheap DNS': True/False,
             'Premium DNS': True/False,
             'FreeDNS': True/False,
             'Nameservers': ['nameserver 1', 'nameserver 2', etc..]
            }

        Raises:
            TypeError -- if domain argument is not str or tuple.
        """
        host_name, tld = self._normalize_domain(domain)

        xml = self._call(
            DOMAINS_GET_NAMESERVERS, {'SLD': host_name, 'TLD': tld}).find(
                self._tag('DomainDNSGetListResult'))

        return {
            'Domain': xml.get('Domain'),
            'Namecheap DNS': xml.get('IsUsingOurDNS').lower() == 'true',
            'Premium DNS': xml.get('IsPremiumDNS').lower() == 'true',
            'FreeDNS': xml.get('IsUsingFreeDNS').lower() == 'true',
            'Nameservers':
                [ns.text for ns in xml.findall(self._tag('Nameserver'))]
        }

    def get_host_records(self):
        pass

    def set_host_records(self):
        pass

    def get_email_forwarding(self):
        pass

    def set_email_forwarding(self):
        pass

    def create_transfer(self):
        pass

    def get_transfer_status(self):
        pass

    def update_transfer_status(self):
        pass

    def get_transfer_list(self):
        pass

    def _normalize_domain(self, domain: typing.Sequence) -> tuple:
        if isinstance(domain, str):
            host_name, _, tld = domain.partition('.')
        elif isinstance(domain, collections.Sequence):
            host_name, tld = domain
        else:
            raise TypeError('Argument "domain" must either be a string or '
                            'a sequence of two strings (domain and TLD).')

        return host_name, tld

    def _build_address_dict(self, address: dict) -> dict:

        result = {}

        # Creates entries like 'RegistrantFirstName' with their values.
        for address_type in ADDRESS_TYPES:

            # Optional parameters
            for param in OPTIONAL_ADDRESS_PARAMS:
                if address.get(param):
                    result[address_type + param] = address.get(param)

            # Required parameters
            for param in REQUIRED_ADDRESS_PARAMS:
                result[address_type + param] = address[param]

        return result
