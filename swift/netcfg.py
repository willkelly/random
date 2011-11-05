#!/usr/bin/python
import sys
import json

if len(sys.argv) != 2:
    sys.stderr.write("Usage: {0} host\n".format(sys.argv[0]))
    sys.exit(1)

host = sys.argv[1]
o = json.loads(open("/opt/djeep/etc/puppet/hosts/%s" % (host)).read())['options']
o.update(json.loads(open("/opt/djeep/etc/puppet/clusters/%s" % (o['cluster'])).read())['options'])

t = """auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
        address {host_ip_address}
        netmask {host_netmask}
        gateway {host_gateway}

auto eth0.{vmnet_vlan}
iface eth0.{vmnet_vlan} inet static
        address {host_vmnet_ip}
        netmask {vmnet_netmask}
        up ifconfig eth0.{vmnet_vlan} up

auto eth0.{mgmt_vlan}
iface eth0.{mgmt_vlan} inet static
        address {host_mgmt_ip}
        netmask {mgmt_netmask}
        up ifconfig eth0.{mgmt_vlan} up""".format(**o)

print t
