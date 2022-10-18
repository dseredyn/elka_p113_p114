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

def printResults(results):
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
        for code, out in res:
            print('***** result code: {}'.format(code))
            print('***** output:\n{}'.format(out))
            if code != 0:
                errors.add(key)

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
    return room

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

    results2 = Results()
    t_list = []
    for i in sorted(results.getAll().keys()):
        if results.getAll()[i][0][0] == 0:
            #print('getNamesIp: {}, {}'.format(i, results.getAll()[i]))
            #print('{}'.format(i))
            cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 192.168.9.{} "uname --nodename"'.format(pw, i)

            #cmd_shell = 'echo "{}" | ssh -s -o ConnectTimeout=2 192.168.9.{} "uname --nodename"'.format(pw, i)
            t = threading.Thread(target=thr_cmd, args=(i, cmd_shell, results2))
            t.start()
            t_list.append(t)

    for t in t_list:
        t.join()

    name_ip_list = []
    for ip in sorted(results2.getAll().keys()):
        name_ip_list.append( (results2.getAll()[ip][0][1].strip(), '192.168.9.{}'.format(ip)) )
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
    for username in ['user', 'uzytkownik']:
        results = {}
        t_list = []
        for ip in ip_list:
            print('{}'.format(ip))
            cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "echo {} | sudo -S rm -rf /home/{}/*/*; echo {} | sudo -S find /home/{} -maxdepth 1 -type f -not -path \'*/\.*\' -delete"'.format(pw, ip, pw, username, pw, username)
            t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
            t.start()
            t_list.append( (t, ip) )

        for t, ip in t_list:
            print('waiting for {}'.format(ip))
            t.join()
    return results

def clearTrash(pw, ip_list):
    for username in ['user', 'uzytkownik']:
        results = {}
        t_list = []
        for ip in ip_list:
            print('{}'.format(ip))
            cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "echo {} | sudo -S rm -rf /home/{}/.local/share/Trash/*"'.format(pw, ip, pw, username, pw, username, pw, username)
            t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, results))
            t.start()
            t_list.append( (t, ip) )

        for t, ip in t_list:
            print('waiting for {}'.format(ip))
            t.join()
    return results

def install(ip_list):
    results = {}
    t_list = []
    for ip in ip_list:
        print('{}'.format(ip))
        cmd_shell = 'ssh -o ConnectTimeout=2 {} "echo {} | sudo -S apt install -y fritzing-data fritzing-parts"'.format(ip, pw)
        t = threading.Thread(target=thr_cmd, args=(ip, cmd_shell, pw, results))
        t.start()
        t_list.append( (t, ip) )

    for t, ip in t_list:
        print('waiting for {}'.format(ip))
        t.join()

    #name_ip_list = []
    #for ip in sorted(results2.keys()):
    #    name_ip_list.append( (results[ip].strip(), '192.168.9.{}'.format(ip)) )
    return results

def shutdown(ip_list, pw):
    results = {}
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
