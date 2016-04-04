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


class WebService (http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send message back to client
        message = "Presente"

        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))

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
        print(gara)
        gara.createDB()

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
    w = GaraMainWindow()
    w.show()
    v = app.exec_()

    # shutdown
    controller.httpd.shutdown()
    sys.exit(v)
