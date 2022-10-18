#!/usr/bin/env python3

import os
import threading
import subprocess
from getpass import getpass
from remote_utils import getNamesIp, selectIPs, clearHomeDir, getNamesForRoom

def main(pw):
    name_ip_list = getNamesIp(pw)
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        print('{}: {}'.format(name, ip))

    room = 'p114'
    names_list = getNamesForRoom(room)

    ip_list = selectIPs(name_ip_list, names_list)
    print('selected ips:')
    print(ip_list)

    results = clearHomeDir(pw, ip_list)
    for key in results:
        print(key)
        print(results[key])
    return 0

if __name__ == "__main__":
    pw = getpass()
    exit( main(pw) )

