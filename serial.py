#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: GPLv3 (see LICENSE)
"""
import sys
import threading
import copy
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *


class SerialManager(QObject):
    lock = threading.RLock()

    def __init__(self, parent, portname):
        super().__init__(parent)
        self.portname = portname

    def connectTo(self):
        self.serial = QSerialPort(self)
        self.serial.readyRead.connect(self.readData)
        self.serial.setPortName(self.portname)
        self.serial.setBaudRate(QSerialPort.Baud2400)
        self.serial.setDataBits(8)
        self.serial.setParity(QSerialPort.NoParity)
        self.serial.setStopBits(1)
        self.serial.setFlowControl(QSerialPort.HardwareControl)
        if self.serial.open(QIODevice.ReadWrite):
            QMessageBox.information(None, "Ok", "Display collegato")
        else:
            QMessageBox.critical(None, "Error", self.serial.errorString())
            return False
        self.gogogo = True
        self.lines = []
        self.index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.asyncDisplay)
        self.timer.start(4000)
        return True

    def asyncDisplay(self):
        if self.gogogo and len(self.lines):
            with self.lock:
                l = self.lines[self.index]
                self.index += 1
                if self.index == len(self.lines):
                    self.index = 0
                self.writeString(l)

    def writeString(self, string):
        code = bytearray([0x04, 0x07, 0x30, 0x30, 0x18, 0x09])
        text = bytearray(string, 'ascii')
        end = bytearray([0x12])
        qb = QByteArray(code+text+end)
        self.serial.write(qb)

    def setSpeed(self, speed):
        assert 0<=speed<=3
        code = bytearray([0x04])
        if speed != 0:
            code += bytearray([0x07, 0x30+speed, 0x30+speed])
        code += bytearray([0x1b, 0x53, 0x42, 0x34+speed, 0x12])
        self.serial.write(QByteArray(code))

    def writeMultipleStrings(self, lines, delay=2.0):
        with self.lock:
            self.index = 0
            self.lines = lines
            self.delay = delay

    def closeSerialPort(self):
        if self.serial.isOpen():
            self.serial.close()
        self.gogogo = False
        self.tr = None

    @pyqtSlot()
    def readData(self):
        pass

    @pyqtSlot(QSerialPort.SerialPortError)
    def error(self, error):
        print(error.errorString())
        self.closeSerialPort()


if __name__ == '__main__':
    l = QSerialPortInfo.availablePorts()
    for s in l:
        d = s.description()
        n = s.portName()
        print(n, d)
        if d == 'FT232R USB UART':
            pass

    app = QApplication(sys.argv)
    s = SerialManager(app, 'cu.usbserial-AJ03K405')
    s.connectTo()
    app.exec_()
