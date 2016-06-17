import typing
from api.session import Session


class DomainAPI:

    def __init__(self, session: Session) -> None:
        self.session = session

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

    def get_info(self, domain: str) -> str:
        return self.session._call(
            'namecheap.domains.getinfo',
            {'DomainName': domain}
        )

    def get_list(self):
        pass

    def get_tld_list(self) -> str:
        return self.session._call('namecheap.domains.getTldlist')

    def check(self, domains: typing.Iterable[str]) -> str:
        return self.session._call(
            'namecheap.domains.check',
            {'DomainList': ','.join(domains)}
        )

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
