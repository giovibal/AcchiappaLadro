#!/bin/bash

cloud_ssh_host=$1
cloud_public_port=$2

while true; do
        ssh -o ConnectTimeout=30 \
            -o BatchMode=yes \
            -o TCPKeepAlive=yes \
            -o ServerAliveInterval=240 \
            -o ExitOnForwardFailure=yes \
            -o UserKnownHostsFile=/dev/null \
            -o StrictHostKeyChecking=no \
            -i \
            /home/pi/.ssh/id_rsa -N -R 0.0.0.0:${cloud_public_port}:localhost:22 ${cloud_ssh_host} &> /dev/null
        sleep 15
done;