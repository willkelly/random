Keystone
========

What is it?
-----------

Keystone is a restful web service that provides authentication services and provide information regarding users, roles, accounts, and services.

Keystone Concepts
-----------------

* Users

* Tenants

* Roles

* Credentials

* Services

* EndpointTemplates

* Endpoints

Significant Roles
-----------------

Admin

: Used by Keystone and Dashboard to allow access to administrative functionality (viewing information about other people's roles, adding/changing users, tenants, endpoints, credentials, and endpointTemplates)

netadmin

:	Used by nova for the following ec2 calls: 

	* AuthorizeSecurityGroupIngress
	* RevokeSecurityGroupIngress
	* CreateSecurityGroup
	* DeleteSecurityGroup
	* AllocateAddress
	* ReleaseAddress
	* AssociateAddress
	* DisassociateAddress

sysadmin

:	Used by nova for the following ec2 calls:

	* GetConsoleOutput
	* DescribeVolumes
	* CreateVolume
	* AttachVolume
	* DetachVolume
	* RunInstances
	* TerminateInstances
	* RebootInstances
	* UpdateInstances
	* StartInstances
	* StopInstances
	* DeleteVolume
	* DeregisterImage
	* RegisterImage
	* ModifyImageAttribute
	* UpdateImage
	* CreateImage

Integrating Keystone
--------------------

Keystone is integrated with other openstack software pieces through the addition of middleware into paste configuration.

A typical nova api-paste.conf for ec2 authentication without keystone will contain a snippet along the lines of the following:

> pipeline = logrequest authenticate cloudrequest authorizer ec2executor

With keystone, the pipeline may look like this:
> pipeline = logrequest totoken tokenauth keystonecontext cloudrequest authorizer ec2executor

The new filters have their own configurations that look like this:

>[filter:tokenauth]
>paste.filter_factory = keystone.middleware.auth_token:filter_factory
>service_protocol = http
>service_host = keystonehostname.domain.com
>service_port = 5000
>auth_host = keystonehostname.domain.com
>auth_port = 5001
>auth_protocol = http
>auth_uri = http://keystonehostname.domain.com:5000/v2.0
>admin_token = 152154125712412
>
>[filter:keystonecontext]
>paste.filter_factory = keystone.middleware.nova_keystone_context:NovaKeystoneContext.factory
>[filter:totoken]
>paste.filter_factory = keystone.middleware.ec2_token:EC2Token.factory
