#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: GPLv3 (see LICENSE)
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *

class SerialManager(QObject):
    def __init__(self, parent):
        super(QObject, self).__init__(parent)

    def connectTo(self):
        self.serial = QSerialPort(self)
        self.serial.readyRead.connect(self.readData)
        self.serial.setPortName("cu.usbserial-AJ03K405")
        self.serial.setBaudRate(QSerialPort.Baud2400)
        self.serial.setDataBits(8)
        self.serial.setParity(QSerialPort.NoParity)
        self.serial.setStopBits(1)
        self.serial.setFlowControl(QSerialPort.NoFlowControl)
        if self.serial.open(QIODevice.ReadWrite):
            print("Connected")
        else:
            QMessageBox.critical(None, "Error", self.serial.errorString())
##            showStatusMessage("Open error")

    def closeSerialPort(self):
        if self.serial.isOpen():
            self.serial.close()

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
    s = SerialManager(app)
    #s.connectTo()
    app.exec_()
