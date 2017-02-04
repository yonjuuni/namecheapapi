from namecheapapi.api.session import Session


class UserAPI:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_pricing(self):
        pass

    def get_balances(self):
        pass

    def change_password(self):
        pass

    def update(self):
        pass

    def create_add_funds_request(self):
        pass

    def get_add_funds_status(self):
        pass

    def create(self):
        pass

    def login(self):
        pass

    def reset_password(self):
        pass

    def create_address(self):
        pass

    def delete_address(self):
        pass

    def get_address_info(self):
        pass

    def get_address_list(self):
        pass

    def set_default_address(self):
        pass

    def update_address(self):
        pass
