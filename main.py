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
from bottle import Bottle, run, get, post, request
from bottle import ServerAdapter, abort, install
from urllib.error import HTTPError
from traceback import format_exc, print_exc

VERSION = '1.0'
webapp = Bottle()


def _e():
    return sys.exc_info()[1]


def getSession(callback):
    def wrapper(*args, **kwargs):
        scoped_session = Gara.activeInstance.scoped_session
        session = scoped_session()
        kwargs['session'] = session
        print("Session created: ", session)
        try:
            body = callback(*args, **kwargs)
            return body
        finally:
            scoped_session.remove()
            print("Session removed")

    return wrapper

webapp.install(getSession)


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
        # self.server.server_close() <--- alternative but causes bad
        # fd exception
        self.server.shutdown()


@webapp.error(401)
@webapp.error(403)
@webapp.error(404)
@webapp.error(409)
def error404(error):
    print(error.body)
    return error.body


@webapp.get('/keepAlive/<judge>')
def keepAlive(judge, session=None):
    if session is None:
        abort(500, {'error': 'server not ready'})

    judge = int(judge)
    configuration = Gara.activeInstance.getConfiguration(session)

    response = gara.state(session)
    response['version'] = VERSION

    ua = request.headers.get('X-User-Auth')
    if ua is None:
        abort(401, {'error': 'no token'})

    if judge <= 0 or judge >= configuration.nJudges:
        # should be 409 but QML XHTTPXmlRequest.status is bugged on android and
        # return 0
        abort(404, {
            'error': 'judge not in range',
            'max': configuration.nJudges})

    conflict = gara.registerJudgeWithUUID(judge, ua)
    if conflict:
        abort(403, {'error': 'judge in use'})
    return response


@webapp.post("/vote")
def vote(session):
    if session is None:
        abort(500, {'error': 'server not ready'})

    ua = request.headers.get('X-User-Auth')
    if ua is None:
        abort(401, {'error': 'no token'})

    trial = int(request.json['trial'])
    judge = int(request.json['judge'])
    user = int(request.json['user'])
    vote = float(request.json['vote'])

    print("Add vote: ", trial, judge, user, vote)

    gara = Gara.activeInstance
    configuration = gara.getConfiguration(session)

    if trial != configuration.currentTrial:
        abort(403, {'code': 1, 'error': 'Trial not accepted'})

    if not (0 <= user <= configuration.nUsers):
        abort(403, {'code': 2, 'error': 'User not valid'})

    if not (0 <= vote <= 10.00):
        abort(403, {'code': 3, 'error': 'Vote not valid'})

    if not gara.validJudge(judge, ua):
        abort(403, {'code': 4, 'error': 'Judge not maching registered uuid'})

    response = gara.addRemoteVote(session, judge, ua, trial, user, vote)
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
        gara.createDB()
        Gara.setActiveInstance(gara)
        self.session = gara.scoped_session()
        self.updateUI()
        print("UI Session:", self.session)

    def updateUI(self):
        configuration = Gara.activeInstance.getConfiguration(self.session)
        print("Configuration:", configuration)

        self.ui.description.setText(configuration.description)

        ntrials = "{}/{}".format(configuration.currentTrial+1,
                                 configuration.nTrials)
        self.ui.currentTrial.setText(ntrials)

        nusers = "{}/{}".format(0, configuration.nUsers)
        self.ui.usersCounter.setText(nusers)

        ngiudici = "{}/{}".format(0, configuration.nJudges)
        self.ui.judgesCounter.setText(ngiudici)

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionNuova_gara.triggered.connect(self.showNuovaGara)
        self.showNuovaGara()

if __name__ == '__main__':
    # empty Gara
    gara = Gara()
    gara.createDB()
    Gara.setActiveInstance(gara)
    assert gara == Gara.activeInstance, "not set"
    assert gara.scoped_session, "scoped_session not set"

    # webservice
    controller = Controller()
    tr = threading.Thread(target=controller.listen)
    tr.start()

    # main ui
    app = QApplication(sys.argv)
    MainWindow = GaraMainWindow()
    MainWindow.setGara(gara)
    MainWindow.show()
    v = app.exec_()

    # shutdown
    controller.shutdown()
    sys.exit(v)
