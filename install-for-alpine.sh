#!/bin/bash
# description       : CloudStack Vines Leaf - Installation Script for Alpine
# author            : Jose Flauzino
# email             : jwvflauzino@inf.ufpr.br
# date              : 20211018
# license           : Apache 2.0
#==============================================================================

echo "Installing requirements"
sed -i -e "s/#h/h/" /etc/apk/repositories
apk update
apk add python3 py3-pip iptables unzip
pip3 install -r requirements.txt

echo "Creating the Vines directory"
mkdir /opt/vines
cp -R ./* /opt/vines

# TODO: run Leaf using some lightweight WSGI server
echo "Configuring autostart"
echo "@reboot cd /opt/vines && python3 management_agent_api.py & > /dev/null" >> /etc/crontabs/root

