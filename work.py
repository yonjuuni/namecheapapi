"""This is a work-in-progress file for namecheapapi module testing.

Namecheap offers two API endpoints: sandbox (for development) and
production (for real world).

You can create a free sandbox account at
https://www.sandbox.namecheap.com/ and activate API access at
https://ap.www.sandbox.namecheap.com/Profile/Tools/ApiAccess
Make sure to add your public IP address in Whitelisted IPs section.

Keep in mind that sandbox domains are not 'real', i.e. they exist only
in Namecheap sandbox (not on the actual Web). With that you may be able
to see google.com as available for registration. At the same time, you
will need to make sure to register your 'virtual' domains if you want to
test domain-specific options, such as renewal, DNS updates, etc.

To start using the API, create a config.py file in the current
directory and fill it in with the following variables:

- API_USER: your Namecheap username
- API_KEY: API key that you got from Namecheap.
- USERNAME: in most cases it would be your Namecheap username.
- CLIENT_IP: your public IP address (MUST be whitelisted in your
    Namecheap account)
- SANDBOX: True/False. Normally should be set to True for testing
    and False on production.

Run 'python3 -i work.py' and feel free to play around. No additional
installs required.
"""
from namecheapapi import DomainAPI
from config import API_USER, API_KEY, USERNAME, CLIENT_IP, SANDBOX, COUPON
from pprint import pprint


api = DomainAPI(
    api_user=API_USER,
    api_key=API_KEY,
    username=USERNAME,
    client_ip=CLIENT_IP,
    sandbox=SANDBOX,
    coupon=COUPON
)

print(api.renew('s1ck.club', check_status_first=True))
