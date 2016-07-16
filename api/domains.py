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
            'IsOwner':
                True if xml.attrib['IsOwner'].lower() == 'true' else False,
            'Full modification rights':
                True if (xml.find(self._tag('Modificationrights')).
                         attrib['All'].lower() == 'true')
                else False
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
            'Enabled':
                True if wg.attrib['Enabled'].lower() == 'true'
                else False,
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
            'Auto-renew': True if pdns.find(
                self._tag('UseAutoRenew')).text.lower() == 'true' else False,
            'Active':
                True if pdns.find(self._tag('IsActive')).text.lower() == 'true'
                else False
        }

        # DNS details
        dns = xml.find(self._tag('DnsDetails'))
        result['DNS'] = {
            'Type': dns.attrib['ProviderType'],
            'Using NC DNS':
                True if dns.attrib['IsUsingOurDNS'].lower() == 'true'
                else False,
            'Host records count': dns.attrib['HostCount'],
            'Email type': dns.attrib['EmailType'],
            'Dynamic DNS':
                True if dns.attrib['DynamicDNSStatus'].lower() == 'true'
                else False,
            'Failover DNS': True if dns.attrib['IsFailover'].lower() == 'true'
                else False,
            'Nameservers': [ns.text for ns in
                            dns.findall(self._tag('Nameserver'))]
        }

        return result

    def get_list(self, _type: str = 'ALL',
                 search_term: str = '') -> typing.List[dict]:
        """Get the list of domains.

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
                    'Expired':
                        True if domain.attrib['IsExpired'].lower() == 'true'
                        else False,
                    'Locked':
                        True if domain.attrib['IsLocked'].lower() == 'true'
                        else False,
                    'Auto-renew':
                        True if domain.attrib['AutoRenew'].lower() == 'true'
                        else False,
                })

        return domains

    # TODO
    def get_tld_list(self) -> str:
        xml = self._call(DOMAINS_GET_TLD_LIST)
        res = {}

    def check(self, domains: typing.Iterable[str]) -> dict:
        """Check domain availability.

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
                True if item.attrib['Available'] == 'true' else False)

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
