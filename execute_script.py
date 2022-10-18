#!/usr/bin/env python3

import os
import sys
import threading
import subprocess
from getpass import getpass
from remote_utils import thr_cmd, getNamesIp, selectIPs, Results, printResults, getNamesForRoom

def extractFilename(path):
    idx = path.rfind('/')
    if idx < 0:
        return path
    # else:
    return path[idx+1:]

def executeScript(ip_list, pw, script_name, sudo):
    results = Results()
    # Copy script
    print('Copying script...')
    t_list = []
    for ip in ip_list:
        print('{}'.format(ip))
        cmd_shell = 'sshpass -p {} scp -o ConnectTimeout=2 {} {}:~/'.format(pw, script_name, ip)
        t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
        t.start()
        t_list.append( (t, ip) )

    for t, ip in t_list:
        print('waiting for {}'.format(ip))
        t.join()

    # Run script
    print('Running script...')
    if sudo:
        sudo_str = 'echo {} | sudo -S '.format(pw)
    else:
        sudo_str = ''
    script_filename = extractFilename(script_name)
    t_list = []
    for ip in ip_list:
        print('{}'.format(ip))
        cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "{} bash ~/{}"'.format(pw, ip, sudo_str, script_filename)
        t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
        t.start()
        t_list.append( (t, ip) )

    for t, ip in t_list:
        print('waiting for {}'.format(ip))
        t.join()

    # Run script
    print('Removing script...')
    if sudo:
        sudo_str = 'echo {} | sudo -S '.format(pw)
    else:
        sudo_str = ''
    script_filename = extractFilename(script_name)
    t_list = []
    for ip in ip_list:
        print('{}'.format(ip))
        cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "{} rm ~/{}"'.format(pw, ip, sudo_str, script_filename)
        t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
        t.start()
        t_list.append( (t, ip) )

    for t, ip in t_list:
        print('waiting for {}'.format(ip))
        t.join()

    return results

def main(pw, script_name, sudo):
    print('Getting IPs and names...')
    name_ip_list = getNamesIp(pw)
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        print('{}: {}'.format(name, ip))

    room = 'p114'
    names_list = getNamesForRoom(room)
#    names_list = ['lab-25']

    #print('name_ip_list: {}'.format(name_ip_list))
    #print('names_list: {}'.format(names_list))

    ip_list = selectIPs(name_ip_list, names_list)
    print('selected ips:')
    print(ip_list)

    results = executeScript(ip_list, pw, script_name, sudo)
    printResults(results)
    return 0

if __name__ == "__main__":
    script_name = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == 'sudo':
        sudo = True
    else:
        sudo = False
    with open('{}'.format(script_name)) as f:
        pass

    pw = getpass()
    exit( main(pw, script_name, sudo) )
