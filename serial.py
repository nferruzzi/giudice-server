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
        #self.setSpeed(0)
        self.writeString("Giudice v1.0                !")
        return True

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
    s = SerialManager(app, 'cu.usbserial-AJ03K405')
    s.connectTo()
    app.exec_()
