#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: MIT (see LICENSE)
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog
from PyQt5.QtCore import QDate
import http.server
import threading
import socketserver
import ui
from gara import *
import json

global MainWindow


class WebService (http.server.BaseHTTPRequestHandler):
    VERSION = '1.0'

    def do_GET(self):
        # Send response status code
        self.send_response(200)

        print(self.headers)

        # Send headers
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Send message back to client
        response = {
            "version": WebService.VERSION,
            "current_trial": 0,
            "max_trial": MainWindow.currentGara.configuration.nTrials,
            "current_user": 0,
            "max_user": MainWindow.currentGara.configuration.nUsers,
            "uuid": MainWindow.currentGara.local_uuid,
            "description": MainWindow.currentGara.configuration.description,
        }

        # Write content as utf-8 data
        self.wfile.write(bytes(json.dumps(response), "utf8"))

    def do_POST(self):
        self.send_response(200)


class Controller (object):
    def listen(self):
        print("listening")
        server_address = ('', 8000)
        self.httpd = socketserver.TCPServer(server_address, WebService)
        self.httpd.serve_forever()
        print("done listening")


class DlgNewGara (QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = ui.Ui_DlgNewGara()
        self.ui.setupUi(self)
        self.setModal(True)
        self.ui.dateEdit.setDate(QDate.currentDate())
        self.ui.numeroGiudici.setCurrentIndex(3)
        self.ui.prove.setCurrentIndex(2)

    def accept(self):
        gara = Gara(description=self.ui.description.text(),
                    nJudges=int(self.ui.numeroGiudici.currentText()),
                    date=self.ui.dateEdit.date(),
                    nTrials=int(self.ui.prove.currentText()),
                    nUsers=int(self.ui.atleti.text()),
                    current=True)
        self.parent().setGara(gara)
        super().accept()

    def reject(self):
        super().reject()


class GaraMainWindow (QMainWindow):
    def showNuovaGara(self):
        # todo check
        dlg = DlgNewGara(self)
        dlg.show()

    def setGara(self, gara):
        self.currentGara = gara
        self.currentGara.createDB()
        self.updateUI()

    def updateUI(self):
        self.ui.description.setText(self.currentGara.configuration.description)

        ntrials = "{}/{}".format(self.currentGara.configuration.currentTrial+1,
                                 self.currentGara.configuration.nTrials)
        self.ui.currentTrial.setText(ntrials)

        nusers = "{}/{}".format(0, self.currentGara.configuration.nUsers)
        self.ui.usersCounter.setText(nusers)

        ngiudici = "{}/{}".format(0, self.currentGara.configuration.nJudges)
        self.ui.judgesCounter.setText(ngiudici)

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionNuova_gara.triggered.connect(self.showNuovaGara)
        self.setGara(Gara())
        self.showNuovaGara()

if __name__ == '__main__':
    # webservice
    controller = Controller()
    tr = threading.Thread(target=controller.listen)
    tr.start()

    # main ui
    app = QApplication(sys.argv)
    MainWindow = GaraMainWindow()
    MainWindow.show()
    v = app.exec_()

    # shutdown
    controller.httpd.shutdown()
    sys.exit(v)
