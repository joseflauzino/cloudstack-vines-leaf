#!/usr/bin/env python

import os
import shlex, subprocess
import json
from flask import jsonify
# verify status of os.system call
verify_status = lambda status: True if status == 0 else False
os.system('touch status | chmod +x status') # Create status file
VINES_PATH = '/opt/vines/'
cmd_path = VINES_PATH + "vnfp/Scripts/"

def read_vnfd():
    with open('/opt/vines/vnfp/Definitions/VNFD.json') as json_file:
        data = json_file.read()
    return json.loads(data)

def generate_cmd(cmd_path, script_name):
    cmd = "sh "+cmd_path+script_name
    print "Cmd: %s" % cmd
    return cmd

def run_cmd(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output[0].rstrip("\n")

def get_memory_usage():
    try:
        # execute 'free' command to get memory usage
        #cmd = check_output(['free', '-t', '-m'])
        cmd = run_cmd(['free', '-t', '-m'])
        # get unused memory value (without swap)
        memory_total = float(cmd.split('\n')[1].split()[1:][0])
        memory_used = float(cmd.split('\n')[1].split()[1:][1])
        memory_usage = float((memory_used/memory_total)*100)
        return memory_usage
    except:
        return None

def get_cpu_usage():
    try:
        with open(VINES_PATH + '/resources/cpu_usage', 'r') as f_cpu:
            cpu_usage = f_cpu.readlines()[-1].replace('\n', '')
            return cpu_usage
    except:
        return None

def get_bandwidth_usage(output):
    try:
        with open(VINES_PATH + '/resources/bandwidth_usage', 'r') as f_bw:
            rx, tx = f_bw.readlines()[-1].replace('\n', '').split(' ')
        if (output == 'rx'):
            return rx
        else:
            return tx
    except:
        return None

# Runs a shell command, checks for success or error and get command response data
def run_shell_cmd(cmd):
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output, error = process.communicate()
	if error:
		return {"status":"ERROR","data":error}
	output = output.rstrip("\n")
	if output == "":
		output = "None"
	return {"status":"OK","data":output}

# Get function status generically 
def get_vnf_function_status(function_name):
	# The status.sh script searches for PID of 'function_name' and returns 'Running' if found, otherwise 'Stopped'
	cmd = "sudo FENDE/Scripts/status.sh %s" % function_name
	response = run_shell_cmd(cmd)
	if response['status']!="OK":
		response['data'] = "Could not run status.sh script: %s" % response['data']
		return response
	return {"status":"OK","data":response['data']}

def build_response(status,data):
	return jsonify(
		{
			"setsfcforwardingresponse": {
				"status": status,
				"data": data
			}
		})