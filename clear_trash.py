#!/usr/bin/env python3

import os
import threading
import subprocess
from getpass import getpass
from remote_utils import getNamesIp, selectIPs, clearTrash

def main(pw):
    name_ip_list = getNamesIp(pw)
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        print('{}: {}'.format(name, ip))

    room = getCurrentRoom()
    names_list = getNamesForRoom(room)

    ip_list = selectIPs(name_ip_list, names_list)
    print('selected ips:')
    print(ip_list)

    print('Run for the following hosts:')
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        if ip in ip_list:
            print('{}: {}'.format(name, ip))

    printResults(results)

    return 0

if __name__ == "__main__":
    pw = getpass()
    exit( main(pw) )

