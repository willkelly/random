#!/bin/bash

NET_DIR="/tmp/network"
if [ ! -e $NET_DIR ]; then
    mkdir $NET_DIR
fi

if [ ! -d $NET_DIR ]; then
    echo $NET_DIR exists but is not a directory
    exit 1
fi

for h in /opt/djeep/etc/puppet/hosts/*; do
    h=$(basename $h)
    ./netcfg.py $h >$NET_DIR/$h.network; 
    scp $NET_DIR/$h.network $h:/etc/network/interfaces
