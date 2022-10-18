#!/usr/bin/env python3

import os
import threading
import subprocess
from getpass import getpass
from remote_utils import thr_cmd, getNamesIp, selectIPs, Results, printResults, getNamesForRoom, getCurrentRoom

def upgrade(ip_list, pw):
    results = Results()
    t_list = []
    for ip in ip_list:
        print('{}'.format(ip))
        cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "echo {} | sudo -S apt update"'.format(pw, ip, pw)
        t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
        t.start()
        t_list.append( (t, ip) )

    for t, ip in t_list:
        print('waiting for {}'.format(ip))
        t.join()

    t_list = []
    for ip in ip_list:
        print('{}'.format(ip))
        cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "echo {} | sudo -S apt upgrade -y"'.format(pw, ip, pw)
        t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
        t.start()
        t_list.append( (t, ip) )

    for t, ip in t_list:
        print('waiting for {}'.format(ip))
        t.join()

    return results

def main(pw):
    name_ip_list = getNamesIp(pw)
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        print('{}: {}'.format(name, ip))

    room = getCurrentRoom()
    names_list = getNamesForRoom(room)

    ip_list = selectIPs(name_ip_list, names_list)
    print('selected ips:')
    print(ip_list)

    results = upgrade(ip_list, pw)

    print('Run for the following hosts:')
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        if ip in ip_list:
            print('{}: {}'.format(name, ip))

    printResults(results)

    return 0

if __name__ == "__main__":
    pw = getpass()
    exit( main(pw) )

