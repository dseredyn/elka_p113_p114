#!/usr/bin/env python3

import os
import threading
import subprocess
from getpass import getpass
from remote_utils import thr_cmd, getNamesIp

def main(pw):
    name_ip_list = getNamesIp(pw)
    for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
        print('{}: {}'.format(name, ip))
    return 0

if __name__ == "__main__":
    pw = getpass()
    exit( main(pw) )

