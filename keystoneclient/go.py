#!/usr/bin/python

import sys
from keystoneclient import KeystoneClient

admin_url = sys.argv.pop(1)
service_url = sys.argv.pop(1)
user = sys.argv.pop(1)
password = sys.argv.pop(1)

ks = KeystoneClient(admin_url=admin_url,
                    service_url=service_url,
                    user=user,
                    password=password)

print ks.version
print ks.tenants.get()
