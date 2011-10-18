Installing Keystone on Ubuntu 10.10
===================================

Installation with RCB packages
------------------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cat <<EOF > /etc/apt/sources.list.d/rcb.list
# rcb                                   
deb  http://ops.monkeypuppetlabs.com/packages maverick diablo-d5
EOF

apt-get update
apt-get upgrade -y
apt-get install keystone
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding a user, tenants, and roles
---------------------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
keystone-manage tenant add AdminTenant
keystone-manage user add admin password AdminTenant
keystone-manage role add Admin
keystone-manage role add Member
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Logging in
----------

~~~~~~~~~~~~~~~~~
curl http://localhost:5000/v2.0/tokens -H 'Content-Type: application/json' -d '{ "passwordCredentials": { "username": "admin", "password": "password" } }'
~~~~~~~~~~~~~~~~~

Checking a user's roles
-----------------------

~~~~~~~~~~~~~~~~~
curl -H 'X-Auth-Token: 4fdef90f-e4bc-425e-b703-116a3f1561ea' -H 'Content-Type: application/json' http://localhost:5001/v2.0/users/admin/roleRefs
~~~~~~~~~~~~~~~~~

Granting a role
---------------

~~~~~~~~~~~~~~~~~
keystone-manage role grant Admin admin
curl -H 'X-Auth-Token: 4fdef90f-e4bc-425e-b703-116a3f1561ea' -H 'Content-Type: application/json' http://localhost:5001/v2.0/users/admin/roleRefs
~~~~~~~~~~~~~~~~~

Adding an Endpoint Template
---------------------------

~~~~~~~~~~~~~~~~~~~
keystone-manage endpointTemplates add RegionOne identity http://keystone.somedomain.com:5000/v2.0 http://keystone-admin.somedomain.com:5001/v2.0 http://keystone-internal.somedomain.com:5000/v2.0 1 1 #enabled, is_global

keystone-manage endpointTemplates list

curl -H 'X-Auth-Token: 4fdef90f-e4bc-425e-b703-116a3f1561ea' -H 'Content-Type: application/json' http://localhost:5001/v2.0/endpointTemplates   
~~~~~~~~~~~~~~~~~~~~

Associating an endpoint with a user
-----------------------------------

~~~~~~~~~~~~~~~
keystone-manage endpoint add admin 1

curl http://localhost:5000/v2.0/tokens -H 'Content-Type: application/json' -d '{ "passwordCredentials": { "username": "admin", "password": "password" } }
~~~~~~~~~~~~~~~

Adding a long lived token
-------------------------

~~~~~~~~~~~~~~
keystone-manage token add 1234567890 admin AdminTenant 2015-02-05T00:00
~~~~~~~~~~~~~~