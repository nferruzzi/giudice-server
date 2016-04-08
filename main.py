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
from bottle import Bottle, run, get, post, request, ServerAdapter, abort

global MainWindow

VERSION = '1.0'
webapp = Bottle()


class MyWSGIRefServer(ServerAdapter):
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        # self.server.server_close() <--- alternative but causes bad fd exception
        self.server.shutdown()


@webapp.get('/keepAlive/<judge>')
def keepAlive(judge):
    # Send message back to client
    response = MainWindow.currentGara.state()
    response['version'] = VERSION
    ua = request.headers.get('X-User-Auth')
    if ua is None:
        abort(401, {'error': 'no token'})
    conflict = MainWindow.currentGara.registerJudgeWithUUID(judge, ua)
    if conflict:
        abort(403, {'error': 'judge in use'})
    return response


class Controller (object):
    def listen(self):
        print("listening")
        self.server = MyWSGIRefServer(host="", port=8000)
        run(webapp, server=self.server)
        print("done listening")

    def shutdown(self):
        self.server.stop()


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
    controller.shutdown()
    sys.exit(v)
