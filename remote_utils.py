#!/usr/bin/env python3

import os
import threading
import subprocess
from getpass import getpass

class Results:
    def __init__(self):
        self.__lock = threading.Lock()
        self.__results = {}

    # Thread safe
    def addResult(self, key, code, out):
        with self.__lock:
            if not key in self.__results:
                self.__results[key] = []
            self.__results[key].append( (code, out) )

    # Thread unsafe
    def getAll(self):
        return self.__results

    def hasAnyErrors(self, key):
        if not key in self.__results:
            return False
        # else:
        for code, out in self.__results[key]:
            if code != 0:
                return True
        return False

    def hasAllErrors(self, key):
        if not key in self.__results:
            return False
        # else:
        for code, out in self.__results[key]:
            if code == 0:
                return False
        return True


def printResults(results, report_any_error=True):
    assert isinstance(results, Results)
    print('*****************************')
    print('*****************************')
    print('********** RESULTS **********')
    print('*****************************')
    print('*****************************')
    errors = set()
    for key in sorted( results.getAll().keys() ):
        res = results.getAll()[key]
        print('********** Results for "{}" **********'.format(key))
        if report_any_error:
            if results.hasAnyErrors(key):
                errors.add(key)
        else:
            if results.hasAllErrors(key):
                errors.add(key)

        for code, out in res:
            print('***** result code: {}'.format(code))
            print('***** output:\n{}'.format(out))

    if errors:
        print('Errors detected for: {}'.format(errors))
    else:
        print('No errors detected')

def thr_cmd(arg, cmd_shell, results):
    assert isinstance(results, Results)
    ret = subprocess.run(cmd_shell, stdout=subprocess.PIPE, shell=True)
    results.addResult(arg, ret.returncode, ret.stdout.decode("utf-8"))

def getCurrentRoom():
    with open('room.txt') as f:
        room = f.read()
    return room.strip()

def getNamesIp(pw):
    t_list = []
    results = Results()
    for i in range(1, 250):
        cmd_shell = 'ping -c 1 192.168.9.{}'.format(i)
        t = threading.Thread(target=thr_cmd, args=(i, cmd_shell, results))
        t.start()
        t_list.append(t)

    for t in t_list:
        t.join()

    all_found_ips = []
    ssh_ips = []

    results2 = Results()
    t_list = []
    for i in sorted(results.getAll().keys()):
        if results.getAll()[i][0][0] == 0:
            #print('getNamesIp: {}, {}'.format(i, results.getAll()[i]))
            #print('{}'.format(i))
            ip_str = '192.168.9.{}'.format(i)
            all_found_ips.append(ip_str)
            cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "uname --nodename"'.format(pw, ip_str)

            #cmd_shell = 'echo "{}" | ssh -s -o ConnectTimeout=2 192.168.9.{} "uname --nodename"'.format(pw, i)
            t = threading.Thread(target=thr_cmd, args=(i, cmd_shell, results2))
            t.start()
            t_list.append(t)

    for t in t_list:
        t.join()

    name_ip_list = []
    for ip in sorted(results2.getAll().keys()):
        ip_str = '192.168.9.{}'.format(ip)
        name_ip_list.append( (results2.getAll()[ip][0][1].strip(), ip_str) )
        ssh_ips.append(ip_str)

    print(all_found_ips)
    print(ssh_ips)
    for ip_str in all_found_ips:

        if not ip_str in ssh_ips:
    # # Get ip that failed for ssh connection
    # for i in sorted(results.getAll().keys()):
    #     if results.getAll()[i][0][0] == 0:
    #         ip_str = '192.168.9.{}'.format(i)
    #         if not ip_str in found_ips:
            print('failed to ssh to ip: {}'.format(ip_str))
        else:
            print('ssh ip: {}'.format(ip_str))

    #print('{}'.format(name_ip_list))
    return name_ip_list

def getNamesForRoom(room):
    result = []
    if room == 'p113':
        for i in range(1,25):
            result.append( 'lab-{}'.format(i) )
        return result
    elif room == 'p114':
        for i in range(25,49):
            result.append( 'lab-{}'.format(i) )
        return result
    # else:
    raise Exception('Wrong room name: "{}"'.format(room))

def clearHomeDir(pw, ip_list):
    pw = 'elkap113p114'

    results = {}

    for username in ['user', 'uzytkownik']:
        results[username] = Results()

        print('Copying home dir template...')
        t_list = []
        for ip in ip_list:
            print('{}'.format(ip))
            cmd_shell = 'sshpass -p {} scp -o ConnectTimeout=2 home_user.tar {}@{}:/tmp/home_user.tar'.format(pw, username, ip)
            t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results[username]))
            t.start()
            t_list.append( (t, ip) )

        for t, ip in t_list:
            print('waiting for {}'.format(ip))
            t.join()

# find /home/user/ -mindepth 1 -maxdepth 1 -name "*" -exec echo '{}' \;
        print('Restoring home dir...')
        t_list = []
        for ip in ip_list:
            print('{}'.format(ip))
            cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {}@{} "cd && find /home/{}/ -mindepth 1 -maxdepth 1 -name \'*\' -exec rm -rf \'{{}}\' \\; && tar -xf /tmp/home_user.tar"'.format(pw, username, ip, username, username, username)
            t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results[username]))
            t.start()
            t_list.append( (t, ip) )

        for t, ip in t_list:
            print('waiting for {}'.format(ip))
            t.join()

        print('Removing home dir template...')
        t_list = []
        for ip in ip_list:
            print('{}'.format(ip))
            cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {}@{} "rm /tmp/home_user.tar"'.format(pw, username, ip)
            t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results[username]))
            t.start()
            t_list.append( (t, ip) )

        for t, ip in t_list:
            print('waiting for {}'.format(ip))
            t.join()

        # t_list = []
        # for ip in ip_list:
        #     print('{}'.format(ip))
        #     cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "echo {} | sudo -S rm -rf /home/{}/*/*; echo {} | sudo -S find /home/{} -maxdepth 1 -type f -not -path \'*/\.*\' -delete"'.format(pw, ip, pw, username, pw, username)
        #     t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
        #     t.start()
        #     t_list.append( (t, ip) )

        # for t, ip in t_list:
        #     print('waiting for {}'.format(ip))
        #     t.join()
    return results

def shutdown(ip_list, pw):
    results = Results()
    t_list = []
    for ip in ip_list:
        print('{}'.format(ip))
        cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "echo {} | sudo -S shutdown -h now"'.format(pw, ip, pw)
        t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
        t.start()
        t_list.append( (t, ip) )

    for t, ip in t_list:
        print('waiting for {}'.format(ip))
        t.join()

    return results

def selectIPs(name_ip_list, names_list):
    result = []
    for name, ip in name_ip_list:
        if name in names_list:
            result.append(ip)
    return result
