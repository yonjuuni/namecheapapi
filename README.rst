============
namecheapapi
============
Python Namecheap API wrapper for simple domain name registration and management.

NOTE: you will need API key from Namecheap to use this module (see below).

Overview
--------

This is work in progress. Official API docs: https://www.namecheap.com/support/api

For now I'm trying not to use anything outside the standard library.
Most methods are more or less well-documented, so don't be shy to use help(). Type hints (PEP 484) are available for every method.
Method names are NOT in 100% match with those from Namecheap, but they are more pythonic and/or hopefully make more sense.

Features
--------
* domain registration/renewal
* domain availability check
* DNS updates
* WHOIS information updates
* get your domain's information
* get a list of your Namecheap domains
* set/remove registrar lock

... and more.


Namecheap API
-------------

Namecheap offers two API endpoints: sandbox (for development & testing) and production (for real world).
You can sign up for a free sandbox account at https://www.sandbox.namecheap.com/ and activate API access at
https://ap.www.sandbox.namecheap.com/Profile/Tools/ApiAccess

Make sure to add your public IP address in Whitelisted IPs section.

Keep in mind that sandbox domains are not 'real', i.e. they exist only
in Namecheap sandbox (not on the actual Web). With that you may be able
to see google.com as available for registration. At the same time, you
will need to make sure to register your 'virtual' domains if you want to
test domain-specific options, such as renewal, DNS updates, etc.


Installation
------------
::

  $ pip install namecheapapi

Example usage
-------------
.. code-block:: python

    # Initialize API
    >>> from namecheapapi import DomainAPI
    >>> api = DomainAPI(
    ...    api_user='api_user',
    ...    api_key='api_key,
    ...    username='username',  # usually the same as api_user
    ...    client_ip='your IP address',
    ...    sandbox=True,  # recommended for testing
    ...    coupon='coupon'  # optional
    ...)
    >>>

    # Check availability of google.com
    >>> api.check('google.com')
    {'google.com': False}

    # Check multiple domains at once
    >>> api.check(['asdfghjhgfdsa.com', 'google.com'])
    {'google.com': False, 'asdfghjhgfdsa.com': True}

    # Register a domain
    >>> address = {
    ...    'FirstName': 'Peter',
    ...    'LastName': 'Griffin',
    ...    'Address1': '31 Spooner St.',
    ...    'City': 'Quahog',
    ...    'StateProvince': 'RI',
    ...    'PostalCode': '00093',
    ...    'Country': 'US',
    ...    'Phone': '+1.123456789',
    ...    'EmailAddress': 'peter@griffin.tv'
    ...}
    >>> api.register('asdfghjhgfdsa.com', address=address)
    {'NonRealTimeDomain': False, 'TransactionID': 1216215, 'WhoisGuardEnabled': False, 'Domain': 'asdfghjhgfdsa.com', 'OrderID': 823656, 'Success': True, 'ChargedAmount': 10.87, 'ID': 117154}

    # Custom query (a raw XML response is returned)
    >>> q = api.raw_query(command='namecheap.domains.transfer.getList', query={})
    >>> print(q)
    <?xml version="1.0" encoding="utf-8"?>
    <ApiResponse Status="OK" xmlns="http://api.namecheap.com/xml.response">
      <Errors />
      <Warnings />
      <RequestedCommand>namecheap.domains.transfer.getlist</RequestedCommand>
      <CommandResponse Type="namecheap.domains.transfer.getList">
        <TransferGetListResult />
        <Paging>
          <TotalItems>0</TotalItems>
          <CurrentPage>1</CurrentPage>
          <PageSize>20</PageSize>
        </Paging>
      </CommandResponse>
      <Server>PHX01SBAPI01</Server>
      <GMTTimeDifference>--4:00</GMTTimeDifference>
      <ExecutionTime>0.01</ExecutionTime>
    </ApiResponse>


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
* domains.get_contacts (namecheap.domains.getContacts)
* domains.set_contacts (namecheap.domains.setContacts)

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

Changelog
---------

0.2.1
~~~~~

* minor bugfixes

0.2
~~~

* documentation update
* domains.get_contacts/set_contacts methods added

0.1.1
~~~~~

* First published working version.

Author
______

`Alex Sanchez <mailto:alex@s1ck.org>`_.
