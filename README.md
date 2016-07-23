# namecheapapi
Python Namecheap API wrapper.

Official docs: https://www.namecheap.com/support/api
See docstring in work.py for current usage tips.

For now I'm trying not to use anything outside the standard library.
This is work in progress, I'm adding more methods as I complete them.
Most methods are more or less well-documented, so don't be shy to use help().
Method names are NOT in 100% match with those from Namecheap, but they are more pythonic and make more sense at times.

Implemented methods:
* domains.check (namecheap.domains.check)
* domains.get_info (namecheap.domains.getInfo)
* domains.get_list (namecheap.domains.getList)
* domains.get_tld_list (namecheap.domains.getTldList)
* domains.renew (namecheap.domains.renew)
* domains.reactivate (namecheap.domains.reactivate)

Next up:
- domains.register
- domains.get_lock (namecheap.domains.getRegistrarLock)
- domains.set_lock (namecheap.domains.setRegistrarLock)
- domains.create_nameserver (namecheap.domains.ns.create)
- domains.delete_nameserver (namecheap.domains.ns.delete)
- domains.update_nameserver (namecheap.domains.ns.update)
- domains.get_nameserver_info (namecheap.domains.ns.getInfo)
