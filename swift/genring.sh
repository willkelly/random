root@infra1:~# cat gen_ring.sh
#!/bin/bash
#pick a proxy node to build the rings on
pn=$(basename $(grep -l swift-proxy /opt/djeep/etc/puppet/hosts/* | head -n1))
#get a string of all swift nodes
sns="$(for s in $(grep -l swift /opt/djeep/etc/puppet/hosts/*); do basename $s; done)"

function get_devices { ssh $(get_ip $1) "df -m | sed 's%/dev/%%' | grep '/srv/node' | awk '{printf(\"%s:%d\n\", \$1, \$2 / 1000 + 1)}'" ; }
function get_ip { cat /opt/djeep/etc/puppet/hosts/$1 | python -mjson.tool | grep host_mgmt_ip | cut -d: -f2 | cut -d\" -f2 ; }

for r in {object,container,account}.builder; do
    ssh $pn "cd /etc/swift; swift-ring-builder $r create 18 3 1"
done

tf=$(tempfile)
echo cd /etc/swift > $tf
z=0
for s in $sns; do
   z=$[ z + 1 ]
   p=5999
   ip=$(get_ip $s)
   devices=$(get_devices $s)
   for r in {object,container,account}.builder; do
       p=$[ p + 1 ]
       for dw in $devices; do
           d=$(echo $dw | cut -d: -f1)
           w=$(echo $dw | cut -d: -f2)
           echo "swift-ring-builder $r add z${z}-$ip:$p/$d $w" >> $tf
       done
   done
done
for r in {object,container,account}.builder; do
    echo swift-ring-builder $r rebalance >> $tf
done

cat $tf | ssh $pn bash
mkdir $tf.$$
scp $pn:/etc/swift/*.gz $tf.$$/
for s in $sns; do
    scp $tf.$$/*.gz $s:/etc/swift/
    ssh $s chown swift: /etc/swift
done
rm $tf
rm -rf $tf.$$
