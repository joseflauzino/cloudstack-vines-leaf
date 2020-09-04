#!/usr/bin/env python

import os
import json
from flask import jsonify
from flask import request
from eve import Eve
from eve.auth import BasicAuth, requires_auth
from subprocess import check_output, call
import time
from util import *

#======================================================
# API Calls
#======================================================

app = Eve()

# -------- Basics (Begin) ----------
@app.route('/api/emsstatus', methods=['GET'])
def ems_status():
    return "Running"
# -------- Basics (End) ----------

# -------- Lifecycle (Begin) ----------
@app.route('/api/install', methods=['POST'])
def install_function():
    status = os.system(generate_cmd(cmd_path,"install.sh"))
    return str(verify_status(status))

@app.route('/api/start', methods=['POST'])
def start_function():
    status = os.system(generate_cmd(cmd_path,"start.sh"))
    if verify_status(status):
        is_running = open('status','w')
        is_running.write("1")
        is_running.close()
    return str(verify_status(status))

@app.route('/api/stop', methods=['POST'])
def stop_function():
    status = os.system(generate_cmd(cmd_path,"stop.sh"))
    if verify_status(status):
        is_running = open('status','w')
        is_running.write("0")
        is_running.close()
    return str(verify_status(status))

@app.route('/api/running', methods=['GET'])
def get_running():
    vnfd = read_vnfd()
    script_name = "get_function_status.sh "
    for op in vnfd['vnfd']['lifecycle']:
        if op['operation'] == 'status':
            script_name = op['file']+' '
    function_name = vnfd['vnfd']['app']
    status = run_cmd("sh "+VINES_PATH+script_name+function_name)
    return str(status) # Running or Stopped

@app.route('/api/push_vnfp', methods=['POST'])
def write_file():
    repo = VINES_PATH+'vnfp.zip'
    with open(repo, 'wb') as f:
        f.write(request.data)
    status = os.system('unzip %s -d %svnfp' % (repo,VINES_PATH))
    return str(verify_status(status))

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    memory = get_memory_usage()
    cpu = get_cpu_usage()
    rx = get_bandwidth_usage('rx')
    tx = get_bandwidth_usage('tx')
    return jsonify(
        {
            "time_ms": 0, 
            "list": [
                {
                    "percent_usage": cpu,
                    "type": "cpu"
                },
                {
                    "percent_usage": 0,
                    "type": "disk"
                },
                {
                    "percent_usage": memory,
                    "type": "memory"
                },
                {
                    "percent_usage": tx,
                    "type": "net_tx"
                },
                {
                    "percent_usage": rx,
                    "type": "net_rx"
                }
            ]
        })
# -------- Lifecycle (End) ----------


# -------- Service Function Chaining (Begin) ----------

@app.route('/api/setsfcforwarding', methods=['POST'])
def setsfcforwarding():

    # parse data
    data = json.loads(request.data)
    last_vnf = data['last_vnf']
    next_vnf = data['next_vnf']
    classifier = data['classifier']

    # Enabling IP forward
    enable_ip_forward_cmd = "sudo bash -c 'echo 1 > /proc/sys/net/ipv4/ip_forward'"
    response = run_shell_cmd(enable_ip_forward_cmd)
    if response["status"] == "ERROR":
        return build_response("error","Could not enable ip_forward")

    for rule in classifier:
        protocol = rule['protocol']
        port = rule['port']

        # Building commands lines
        #enable_forward_cmd = "sudo iptables -A FORWARD -d %s -j ACCEPT" % (last_vnf)
        enable_forward_cmd = "sudo iptables -A FORWARD -j ACCEPT"
        config_forward_cmd = "sudo iptables -t nat -A PREROUTING -p %s --dport %s -j DNAT --to %s" % (protocol, port, next_vnf)

        # Adding FORWARD rule
        response = run_shell_cmd(enable_forward_cmd)
        if response["status"] == "ERROR":
            return build_response("error","Could not enable add forward rule")

        # Adding PREROUTING rule
        response = run_shell_cmd(config_forward_cmd)
        if response["status"] == "ERROR":
            return build_response("error","Could not add PREROUTING rule")

    return build_response("success","VNF classifiers have been configured")


@app.route('/api/deletesfcforwarding', methods=['POST'])
def deletesfcforwarding():
    # build command lines
    clean_iptables_cmd = "sudo iptables -F"
    clean_nat_iptables_cmd = "sudo iptables -t nat -F"
    disable_ip_forward_cmd = "sudo bash -c 'echo 0 > /proc/sys/net/ipv4/ip_forward'"

    response = run_shell_cmd(disable_ip_forward_cmd)
    if response["status"] == "ERROR":
        return build_response("error","Could not disable ip_forward")
    response = run_shell_cmd(clean_iptables_cmd)
    if response["status"] == "ERROR":
        return build_response("error","Could not clean iptables")
    response = run_shell_cmd(clean_nat_iptables_cmd)
    if response["status"] == "ERROR":
        return build_response("error","Could not clean iptables (NAT table)")

    return build_response("success","SFC forwarding deleted")

# -------- Service Function Chaining (End) ----------


if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000)