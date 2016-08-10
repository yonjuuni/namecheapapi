============
namecheapapi
============
Python Namecheap API wrapper.

Work in progress, see docstring in work.py for current usage tips. Official docs: https://www.namecheap.com/support/api

For now I'm trying not to use anything outside the standard library.
Most methods are more or less well-documented, so don't be shy to use help(). Also type hints (PEP 484) are available for every method.
Method names are NOT in 100% match with those from Namecheap, but they are more pythonic and make more sense at times.

Installation
------------
  $ pip install namecheapapi

Example usage
-------------
::

    from namecheapapi import DomainAPI

    api = DomainAPI(
        api_user='api_user',
        api_key='api_key,
        username='username',  # usually the same as api_user
        client_ip='your IP address',
        sandbox=True,  # recommended for testing
        coupon='coupon'  # optional
    )

    print(api.check('google.com'))

    address = {
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

    print(api.register('adsasdasasdsadasdsad.com', address=address))

Implemented methods
-------------------
* domains.register (namecheap.domains.create)
* domains.check (namecheap.domains.check)
* domains.get_info (namecheap.domains.getInfo)
* domains.get_list (namecheap.domains.getList)
* domains.get_tld_list (namecheap.domains.getTldList)
* domains.renew (namecheap.domains.renew)
* domains.reactivate (namecheap.domains.reactivate)
* domains.get_lock (namecheap.domains.getRegistrarLock)
* domains.set_lock (namecheap.domains.setRegistrarLock)
* domains.get_nameservers (namecheap.domains.dns.getList)
* domains.set_nameservers (namecheap.domains.dns.setCustom, namecheap.domains.dns.setDefault)

Next up
-------
* domains.create_nameserver (namecheap.domains.ns.create)
* domains.delete_nameserver (namecheap.domains.ns.delete)
* domains.update_nameserver (namecheap.domains.ns.update)
* domains.get_nameserver_info (namecheap.domains.ns.getInfo)
* domains.get_host_records (namecheap.domains.dns.getHosts)
* domains.set_host_records (namecheap.domains.dns.setHosts)

Testing
-------
(does have one dependency)

1. Install nosetests (``pip install nose``)
2. Create ``config.py`` in ``namecheapapi/tests/`` directory, fill it in:

  * ``API_KEY`` = 'string' -- API key that you got from Namecheap
  * ``API_USER`` = 'string' -- your Namecheap username
  * ``USERNAME`` = 'string' -- in most cases it would be your Namecheap username
  * ``CLIENT_IP`` = 'string' -- your public IP address (MUST be whitelisted in your Namecheap account)
  * ``SANDBOX`` = True (recommended!)
  * ``COUPON`` = 'string' -- coupon code if you have any, '' otherwise
  * ``DOMAIN`` = 'string' -- a domain name you ALREADY HAVE in your Namecheap account

3. Run ``nosetests /path/to/namecheapapi/dir``

I'll keep adding more tests with time.
