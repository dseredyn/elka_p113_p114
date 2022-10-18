#!/usr/bin/env python3

import os
import threading
import subprocess
from getpass import getpass
from remote_utils import getNamesIp, selectIPs, clearHomeDir, getCurrentRoom, getNamesForRoom

def printResults(results):
    print('*****************************')
    print('*****************************')
    print('********** RESULTS **********')
    print('*****************************')
    print('*****************************')
    errors = set()
    usernames = list(results.keys())
    for key in sorted( results[usernames[0]].getAll().keys() ):
        selected_username = None
        for username in usernames:
            if not results[username].hasAnyErrors(key):
                selected_username = username
                break

        if selected_username is None:
            errors.add(key)
            for username in usernames:
                res = results[username].getAll()[key]
                print('********** Results for "{}" **********'.format(key))
                for code, out in res:
                    print('***** result code: {}'.format(code))
                    print('***** output:\n{}'.format(out))
        else:
            res = results[selected_username].getAll()[key]
            print('********** Results for "{}" **********'.format(key))
            for code, out in res:
                print('***** result code: {}'.format(code))
                print('***** output:\n{}'.format(out))

    if errors:
        print('Errors detected for: {}'.format(errors))
    else:
        print('No errors detected')

def main(pw):
    name_ip_list = getNamesIp(pw)
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        print('{}: {}'.format(name, ip))

    room = getCurrentRoom()
    names_list = getNamesForRoom(room)

    ip_list = selectIPs(name_ip_list, names_list)
    print('selected ips:')
    print(ip_list)

    results = clearHomeDir(pw, ip_list)

    print('Run for the following hosts:')
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        if ip in ip_list:
            print('{}: {}'.format(name, ip))

    printResults(results)

    return 0

if __name__ == "__main__":
    pw = getpass()
    exit( main(pw) )

