#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 2017 2018 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: GPLv3 (see LICENSE)
"""
from PyQt5.QtCore import *

class FakeSerialPort(QObject):
    SerialPortError = str

class FakeSerialPortInfo(QObject):
    @classmethod
    def availablePorts(self):
        return []

try:
    from PyQt5.QtSerialPort import *
    MySerialPort = QSerialPort
    MySerialPortInfo = QSerialPortInfo
    print("Loaded QSerialPort")
except:
    MySerialPort = FakeSerialPort
    MySerialPortInfo = FakeSerialPortInfo
    print("Loaded fake QSerialPort")

    

