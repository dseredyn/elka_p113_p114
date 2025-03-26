#!/usr/bin/env python3

# Author: Dawid Seredyński
# License: Apache 2.0

import os

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout,\
    QHBoxLayout, QGroupBox, QScrollArea, QPushButton, QComboBox, QCheckBox

from getpass import getpass
from remote_utils import thr_cmd, getNamesIp, getCurrentRoom, getNamesForRoom,\
    selectIPs, Results

# GUI ma następujące funkcje:
# 1. Widok na listę komputerów z infomracją:
#   - czy jest online (czy jest możliwe połączenie po ssh)
#   - adres ip
#   - [nazwy użytkowników i kto jest obecnie zalogowany]
#   - wynik uruchomienia skryptu - ogólnie w polu, a szczegółowo w osobnym oknie
# 2. Uruchomienie skryptu na wybranych komputerach (możliwe zaznaczenie
#    wszystkich, żadnego, lub pojedynczych)

scripts_dir = 'remote_scripts'

def readMachines():
    with open('machines.txt', 'r') as f:
        lines = f.readlines()
    result = []
    for l in lines:
        line = l.strip()
        if line.startswith('#'):
            continue
        items = line.split()
        result.append( (items[0], items[1]) )
    return result

import socket

def getThisMachineIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    print(ip)
    s.close()
    return ip

def extractFilename(path):
    idx = path.rfind('/')
    if idx < 0:
        return path
    # else:
    return path[idx+1:]

def executeScript(ip_list, pw, script_name, sudo, server_ip):
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
        cmd_shell = 'sshpass -p {} ssh -o ConnectTimeout=2 {} "{} bash ~/{} {}"'.format(pw, ip, sudo_str, script_filename, server_ip)
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

class MachinePanel(QGroupBox):
    def __init__(self, name):
        super(MachinePanel, self).__init__()

        self.__name = name
        self.__ip = None

        self.initUI()

    def initUI(self):
        vbox = QHBoxLayout()
        #label_name = QLabel('{}'.format(self.__name))
        self.check_box = QCheckBox('{}'.format(self.__name))
        self.label_ip = QLabel('{}'.format(self.__ip))
        self.label_status = QLabel()
        vbox.addWidget(self.check_box)
        #vbox.addWidget(label_name)
        vbox.addWidget(self.label_ip)
        vbox.addWidget(self.label_status)
        vbox.addStretch(1)
        self.setLayout(vbox)
        #return groupBox

    def select(self):
        self.check_box.setChecked(True)

    def unselect(self):
        self.check_box.setChecked(False)

    def isSelected(self):
        return self.check_box.isChecked()

    def getMachineName(self):
        return self.__name

    def getMachineIp(self):
        return self.__ip

    def updateIp(self, ip):
        self.__ip = ip
        self.label_ip.setText('{}'.format(self.__ip))

    def setStatus(self, status_str):
        self.label_status.setText(status_str)

class LabManager(QWidget):

    def __init__(self, pw):
        super(LabManager, self).__init__()
        self.__panels = []
        self.__pw = pw
        self.initUI()

    def getScriptNames(self):
        result = []
        for path in os.listdir(scripts_dir):
            # check if current path is a file
            if os.path.isfile(os.path.join(scripts_dir, path)):
                result.append(path)
        return result

    def button_update_clicked(self):
        self.updateMachineList()

    def button_all_clicked(self):
        #print('button_all_clicked')
        for panel in self.__panels:
            panel.select()

    def button_none_clicked(self):
        #print('button_none_clicked')
        for panel in self.__panels:
            panel.unselect()

    def button_exec_clicked(self):
        print('Executing script "{}" for:'.format(
                                            self.combo_script.currentText()))
        ip_list = []
        for panel in self.__panels:
            if panel.isSelected() and not panel.getMachineIp() is None:
                print('{}: {}'.format(panel.getMachineName(),
                                                        panel.getMachineIp()))
                ip_list.append( panel.getMachineIp() )
                panel.setStatus('waiting for result...')

        server_ip = getThisMachineIp()
        sudo = self.combo_script.currentText().startswith('sudo_')
        script_name = 'remote_scripts/{}'.format(
                                            self.combo_script.currentText())
        results = executeScript(ip_list, self.__pw, script_name, sudo, server_ip)
        self.publishResults(results)

    def publishResults(self, results):
        assert isinstance(results, Results)

        for panel in self.__panels:
            ip = panel.getMachineIp()
            if ip in results.getAll():
                res = results.getAll()[ip]
                if results.hasAnyErrors(ip):
                    panel.setStatus('error')
                else:
                    panel.setStatus('ok')

                with open('output/{}.txt'.format(panel.getMachineName()), 'w') as f:
                    for code, out in res:
                        f.write('***** result code: {}\n'.format(code))
                        f.write('***** output:\n{}\n'.format(out))
            else:
                panel.setStatus('')

        # errors = set()
        # for key in sorted( results.getAll().keys() ):
        #     res = results.getAll()[key]
        #     ip = key


        #     print('********** Results for "{}" **********'.format(key))
        #     if report_any_error:
        #         if results.hasAnyErrors(key):
        #             errors.add(key)
        #     else:
        #         if results.hasAllErrors(key):
        #             errors.add(key)

        #     for code, out in res:
        #         print('***** result code: {}'.format(code))
        #         print('***** output:\n{}'.format(out))

        # if errors:
        #     print('Errors detected for: {}'.format(errors))
        # else:
        #     print('No errors detected')

    def initUI(self):
        main_layout = QVBoxLayout(self)

        script_widget = QWidget()
        script_layout = QHBoxLayout(script_widget)
        button_update = QPushButton('Update list')
        button_update.clicked.connect(self.button_update_clicked)
        button_all = QPushButton('Select all')
        button_all.clicked.connect(self.button_all_clicked)
        button_none = QPushButton('Select none')
        button_none.clicked.connect(self.button_none_clicked)
        self.combo_script = QComboBox()

        for script_name in sorted(self.getScriptNames()):
            self.combo_script.addItem(script_name)
        button_exec = QPushButton('Execute')
        button_exec.clicked.connect(self.button_exec_clicked)

        script_layout.addWidget(button_update)
        script_layout.addWidget(button_all)
        script_layout.addWidget(button_none)
        script_layout.addWidget(self.combo_script)
        script_layout.addWidget(button_exec)

        # Execute script
        main_layout.addWidget(script_widget)

        # List of machines
        scroll = QScrollArea(self)
        main_layout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scrollContent = QWidget(scroll)

        self.scrollLayout = QVBoxLayout(scrollContent)
        scroll.setWidget(scrollContent)

    def addPanel(self, panel):
        self.__panels.append(panel)
        self.scrollLayout.addWidget(panel)

    def updateMachineList(self):
        # Fake list for tests
        #name_ip_list = [('lab-01', '123.123.1.1'), ('lab-02', '123.123.1.2'),
        #    ('lab-03', '123.123.1.3'), ('lab-04', '123.123.1.4')]

        name_ip_list = getNamesIp(self.__pw)

        name_ip_dict = {}
        for name, ip in sorted(name_ip_list, key=lambda x:x[0]):
            # print('{}: {}'.format(name, ip))
            name_ip_dict[name] = ip

        for panel in self.__panels:
            name = panel.getMachineName()
            if name in name_ip_dict:
                panel.updateIp(name_ip_dict[name])
            else:
                panel.updateIp(None)

import threading
import functools
from http.server import HTTPServer, SimpleHTTPRequestHandler

def http_server_thread_function(httpd):
    print('Running http server')
    httpd.serve_forever()

def main():
    # Try to read password form file
    try:
        with open('do_not_commit_passwd.txt', 'r') as f:
            pw = f.read()
            print('Read password form file')
    except:
        pw = getpass()

    app = QApplication([])
    lab_manager = LabManager(pw)
    lab_manager.show()

    machines = readMachines()
    for name, room in machines:
        panel = MachinePanel(name)
        lab_manager.addPanel(panel)

    Handler = functools.partial(SimpleHTTPRequestHandler, directory='{}/http_shared/'.format(os.getcwd()))
    httpd = HTTPServer(('', 8000), Handler)
    x = threading.Thread(target=http_server_thread_function, args=(httpd,))
    x.start()

    app.exec_()

    print('Stopping http server')
    httpd.shutdown()
    x.join()

    return 0

if __name__ == "__main__":
    exit( main() )
