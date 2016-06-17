from api.session import Session


class SslAPI:

    def __init__(self, session: Session) -> None:
        self.session = session

    def activate(self):
        pass

    def get_info(self):
        pass

    def parse_csr(self):
        pass

    def get_approver_email_list(self):
        pass

    def get_list(self):
        pass

    def purchase(self):
        pass

    def renew(self):
        pass

    def resend_approver_email(self):
        pass

    def resend(self):
        pass

    def reissue(self):
        pass

    def purchase_more_sans(self):
        pass

    def revoke(self):
        pass
