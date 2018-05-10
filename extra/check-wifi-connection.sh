#!/bin/bash

#==============================
wlan='wlan0'
gateway=$1
alias dhclient='/sbin/dhclient'
alias ifconfig='/sbin/ifconfig'
#==============================

# Verify that a gateway IP address is given.
if [ ! -n "${gateway}" ]
then
    echo "Usage: $0 192.168.1.1"
    echo "       Where 192.168.1.1 is the IP address of the gateway to test against."
    exit 2
fi

# Ping the gateway using only the wireless device
ping -I ${wlan} -c3 ${gateway} > /dev/null 

# Check the return code. Anything other than 0 means we had an erroring pinging the gateway
if [ $? != 0 ]
then
    echo "Could not ping Gateway. Restarting wireless interface."
    # Restart the wireless interface
    ifconfig ${wlan} down
    sleep 5
    ifconfig ${wlan} up
    sleep 5
    dhclient ${wlan}
else
    echo "Gateway successfully pinged. Do not need to restart wireless interface."
fi
