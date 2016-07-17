import typing
from datetime import datetime
from math import ceil
from xml.etree.ElementTree import fromstring
from api.session import Session
from api.commands import *


class DomainAPI(Session):

    def register(self):
        pass

    def renew(self, domain: str, years: int,
              check_status_first: bool = False):
        """Domain renewal option.

        If check_status_first is set to True, get_info() will be
        called first to check if the domain is expired. If it is,
        reactivate() will be called instead.
        """
        pass

    def reactivate(self, domain: str):
        pass

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
            'Domain': xml.attrib['DomainName'],
            'Owner': xml.attrib['OwnerName'],
            'Status': xml.attrib['Status'],
            'ID': xml.attrib['ID'],
            'IsOwner': xml.attrib['IsOwner'].lower() == 'true',
            'Full modification rights':
                xml.find(self._tag('Modificationrights')).
                attrib['All'].lower() == 'true'
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
            'Enabled': wg.attrib['Enabled'].lower() == 'true',
            'Expiration':
                datetime.strptime(wg.find(self._tag('ExpiredDate')).text,
                                  '%m/%d/%Y'),
            'ID': wg.find(self._tag('ID')).text,
            'Email':
                wg.find(self._tag('EmailDetails')).attrib['WhoisGuardEmail'],
            'Forwarded to':
                wg.find(self._tag('EmailDetails')).attrib['ForwardedTo'],
            'Last email auto-change date':
                wg.find(self._tag('EmailDetails')).attrib[
                'LastAutoEmailChangeDate']
                if wg.find(self._tag('EmailDetails')).attrib[
                    'LastAutoEmailChangeDate']
                else None,
            'Email auto-change frequency':
                wg.find(self._tag('EmailDetails')).attrib[
                    'AutoEmailChangeFrequencyDays']
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
            'Type': dns.attrib['ProviderType'],
            'Using NC DNS': dns.attrib['IsUsingOurDNS'].lower() == 'true',
            'Host records count': dns.attrib['HostCount'],
            'Email type': dns.attrib['EmailType'],
            'Dynamic DNS': dns.attrib['DynamicDNSStatus'].lower() == 'true',
            'Failover DNS': dns.attrib['IsFailover'].lower() == 'true',
            'Nameservers': [ns.text for ns in
                            dns.findall(self._tag('Nameserver'))]
        }

        return result

    def get_list(self, _type: str = 'ALL',
                 search_term: str = '') -> typing.List[dict]:
        """Get the list of domains.

        https://www.namecheap.com/support/api/methods/domains/get-list.aspx

        Arguments:
            _type - possible values: 'ALL', 'EXPIRING', 'EXPIRED'
            search_term - keyword to look for in the domain list.

        Returns:
            A list containing dicts with domain information.
        """

        domains = []

        # A check on the total domain number (minimal PageSize is 10)
        xml = self._call(
            DOMAINS_GET_LIST, {'ListType': _type,
                               'SearchTerm': search_term,
                               'PageSize': 10}).find(
            self._tag('Paging'))
        total_domains = int(xml.find(self._tag('TotalItems')).text)

        # A call is sent for every 100-item page
        # TODO: check performance on big accounts
        for page in range(1, ceil(total_domains / 100) + 1):

            xml = self._call(
                DOMAINS_GET_LIST, {'ListType': _type,
                                   'SearchTerm': search_term,
                                   'Page': page,
                                   'PageSize': 100}).find(
                self._tag('DomainGetListResult'))

            for domain in xml.findall(self._tag('Domain')):
                domains.append({
                    'Domain': domain.attrib['Name'],
                    'ID': domain.attrib['ID'],
                    'Owner': domain.attrib['User'],
                    'Creation': datetime.strptime(domain.attrib['Created'],
                                                  '%m/%d/%Y'),
                    'Expiration': datetime.strptime(domain.attrib['Expires'],
                                                    '%m/%d/%Y'),
                    'WhoisGuard': domain.attrib['WhoisGuard'],
                    'Expired': domain.attrib['IsExpired'].lower() == 'true',
                    'Locked': domain.attrib['IsLocked'].lower() == 'true',
                    'Auto-renew': domain.attrib['AutoRenew'].lower() == 'true',
                })

        return domains

    def get_tld_list(self) -> typing.Dict[str, dict]:
        """Get TLD list

        https://www.namecheap.com/support/api/methods/domains/get-tld-list.aspx

        NOTE: Namecheap strongly recommend that you cache this API
        response to avoid repeated calls.

        Returns:
            A dict:
            {'tld': {details...},
             'tld2': {details...}
            }
        """
        xml = self._call(DOMAINS_GET_TLD_LIST).find(self._tag('Tlds'))

        res = {}

        for tld in xml.findall(self._tag('Tld')):
            tld_name = tld.attrib['Name']
            res[tld_name] = tld.attrib
            res[tld_name]['Description'] = tld.text

            # Normalize dict values
            for key in res[tld_name]:
                if res[tld_name][key].lower() == 'false':
                    res[tld_name][key] = False
                elif res[tld_name][key].lower() == 'true':
                    res[tld_name][key] = True
                elif res[tld_name][key].lower() == '':
                    res[tld_name][key] = None
                else:
                    try:
                        int(res[tld_name][key])
                    except ValueError:
                        pass
                    else:
                        res[tld_name][key] = int(res[tld_name][key])

        return res

    def check(self, domains: typing.Iterable[str]) -> dict:
        """Check domain availability.

        https://www.namecheap.com/support/api/methods/domains/check.aspx

        Arguments:
        domains -- any iterable (str for single domain; list, set,
        dict for multiple domains)

        Returns:
        Dict with boolean values for domain availability.
        E.g.:
            {'google.com': False, 'yourawesomedomain.name': True}

        """
        if isinstance(domains, str):
            domains = [domains, ]
        xml = self._call(DOMAINS_CHECK, {'DomainList': ','.join(domains)})

        result = {}
        for item in xml.findall(self._tag('DomainCheckResult')):
            result[item.attrib['Domain']] = (
                item.attrib['Available'] == 'true')

        return result

    def get_contacts(self):
        pass

    def set_contacts(self):
        pass

    def get_lock(self):
        pass

    def set_lock(self):
        pass

    def create_nameserver(self):
        pass

    def delete_nameserver(self):
        pass

    def update_nameserver(self):
        pass

    def get_nameserver_info(self):
        pass

    def set_nameservers(self, default: bool = False):
        """default=True will set Namecheap DNS
        """
        pass

    def get_nameservers(self):
        pass

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
