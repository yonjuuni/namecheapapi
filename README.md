# namecheapapi
Python Namecheap API wrapper.

Work in progress, see docstring in work.py for current usage tips. Official docs: https://www.namecheap.com/support/api

For now I'm trying not to use anything outside the standard library.
Most methods are more or less well-documented, so don't be shy to use help(). Also type hints (PEP 484) are available for every method.
Method names are NOT in 100% match with those from Namecheap, but they are more pythonic and make more sense at times.

Implemented methods:
* domains.check (namecheap.domains.check)
* domains.get_info (namecheap.domains.getInfo)
* domains.get_list (namecheap.domains.getList)
* domains.get_tld_list (namecheap.domains.getTldList)
* domains.renew (namecheap.domains.renew)
* domains.reactivate (namecheap.domains.reactivate)
* domains.get_lock (namecheap.domains.getRegistrarLock)
* domains.set_lock (namecheap.domains.setRegistrarLock)

Next up:
- domains.register (namecheap.domains.create)
- domains.create_nameserver (namecheap.domains.ns.create)
- domains.delete_nameserver (namecheap.domains.ns.delete)
- domains.update_nameserver (namecheap.domains.ns.update)
- domains.get_nameserver_info (namecheap.domains.ns.getInfo)

Required for v0.01:
- domains.get_host_records
- domains.set_host_records
- domains.get_nameservers
- domains.set_nameservers


Testing.

1. Install nosetests (pip3 install nose)
2. Create config.py in namecheapapi/tests/ directory, fill it in:
* API_KEY = 'string' -- API key that you got from Namecheap
* API_USER = 'string' -- your Namecheap username
* USERNAME = 'string' -- in most cases it would be your Namecheap username
* CLIENT_IP = 'string' -- your public IP address (MUST be whitelisted in your Namecheap account)
* SANDBOX = True (recommended!)
* COUPON = 'string' -- coupon code if you have any, '' otherwise
* DOMAIN = 'string' -- a domain name you ALREADY HAVE in your Namecheap account
3. Run 'nosetests /path/to/namecheapapi/dir'

I'll keep adding more tests with time.
