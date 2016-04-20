#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: GPLv3 (see LICENSE)
"""
import sys
import copy
import time
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *


class SerialManager(QObject):

    serial_disconnected = pyqtSignal(name='serialDisconnected')

    def __init__(self, parent, portname):
        super().__init__(parent)
        self.portname = portname

    def connectTo(self):
        self.serial = QSerialPort(self)
        self.serial.setPortName(self.portname)
        self.serial.setBaudRate(QSerialPort.Baud2400)
        self.serial.setDataBits(8)
        self.serial.setParity(QSerialPort.NoParity)
        self.serial.setStopBits(1)
        # does not work on windows for some reason with the adapter we got
        # self.serial.readyRead.connect(self.readData)
        # self.serial.readChannelFinished.connect(self.endReadData)
        # self.serial.setFlowControl(QSerialPort.HardwareControl)
        if self.serial.open(QIODevice.ReadWrite):
            QMessageBox.information(None, "Ok", "Display collegato")
        else:
            QMessageBox.critical(None, "Error", self.serial.errorString())
            return False
        self.lines = []
        self.index = 0
        self.timer = None
        self.timeTimer = QTimer()
        self.timeTimer.timeout.connect(self.timeLogic)
        self.timeTimer.start(500)
        self.currentTime = None
        return True

    def asyncDisplay(self):
        if len(self.lines):
            if self.index == len(self.lines):
                self.writeString("     ")
                self.timer.stop()
                QTimer.singleShot(5000, self.resetTimer)
            else:
                l = self.lines[self.index]
                self.writeString(l)
                self.index += 1

    def resetTimer(self):
        self.lines = []
        self.currentTime = None

    def timeLogic(self):
        if len(self.lines) == 0:
            current_time = datetime.datetime.now().time().strftime('%H:%M')
            if self.currentTime != current_time:
                self.writeString(current_time)
                self.currentTime = current_time

    def writeString(self, string):
        code = bytearray([0x04, 0x07, 0x30, 0x30, 0x18, 0x09])
        text = bytearray(string, 'ascii')
        end = bytearray([0x12])
        qb = QByteArray(code+text+end)

        w = self.serial.write(qb)
        self.serial.flush()

        # checks doesn't look to work on windows
        if 0:
            self.serial.waitForReadyRead(1000)
            r = self.serial.readAll()
            if len(r) == 0:
                w = 0

        if w == 0:
            self.parent().ui.displayPreview.setText("Il display non risponde, assicurarsi che sia acceso e collegato.")
            self.serial_disconnected.emit()
        else:
            self.parent().ui.displayPreview.setText(string)

    def setSpeed(self, speed):
        assert 0 <= speed <=3, "Wrong speed"
        code = bytearray([0x04])
        if speed != 0:
            code += bytearray([0x07, 0x30+speed, 0x30+speed])
        code += bytearray([0x1b, 0x53, 0x42, 0x34+speed, 0x12])
        self.serial.write(QByteArray(code))

    def writeMultipleStrings(self, lines):
        s = QSettings()
        repeat = s.value("display/repeat", 3)
        if self.timer:
            self.timer.stop()
        self.timer = QTimer()
        self.timer.timeout.connect(self.asyncDisplay)
        self.timer.start(s.value("display/delay", 4000))
        self.index = 0
        self.lines = lines * repeat
        self.asyncDisplay()

    def closeSerialPort(self):
        if self.timer:
            self.timer.stop()
        if self.serial.isOpen():
            self.serial.close()

    @pyqtSlot()
    def readData(self):
        print("Data ready")

    @pyqtSlot()
    def endReadData(self):
        print("Device closed")
        self.parent().ui.displayPreview.setText("Il display non risponde, assicurarsi che sia acceso e collegato.")
        self.serial_disconnected.emit()

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
    s = SerialManager(app, 'COM1') #cu.usbserial-AJ03K405')
    s.connectTo()
    s.writeString('UE')
    s.serial.flush()
    #app.exec_()
