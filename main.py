#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: MIT (see LICENSE)
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import http.server
import threading
import socketserver
import ui
import pathlib
import json
from gara import *
from bottle import Bottle, run, get, post, request
from bottle import ServerAdapter, abort, install
from urllib.error import HTTPError

VERSION = '1.0'
webapp = Bottle()
_translate = QCoreApplication.translate


def _e():
    return sys.exc_info()[1]


def getSqliteConnection(callback):
    def wrapper(*args, **kwargs):
        gara = Gara.activeInstance
        if gara is None:
            abort(500, {'error': 'server not configured'})

        connection = gara.getConnection()
        if connection is None:
            abort(500, {'error': 'server internal error'})

        kwargs['connection'] = connection
        kwargs['gara'] = gara

        print("Gara: ", gara)
        print("Connection created: ", connection)

        try:
            body = callback(*args, **kwargs)
            return body
        finally:
            connection.close()
            print("Connection closed")
            pass

    return wrapper

webapp.install(getSqliteConnection)


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
def keepAlive(judge, connection=None, gara=None):
    judge = int(judge)
    configuration = Gara.activeInstance.getConfiguration(connection)

    response = gara.getState(connection)
    response['version'] = VERSION

    ua = request.headers.get('X-User-Auth')
    if ua is None:
        abort(401, {'error': 'no token'})

    if judge <= 0 or judge > configuration['nJudges']:
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
def vote(connection, gara):
    ua = request.headers.get('X-User-Auth')
    if ua is None:
        abort(401, {'error': 'no token'})

    trial = int(request.json['trial'])
    judge = int(request.json['judge'])
    user = int(request.json['user'])
    vote = float(request.json['vote'])

    print("Add vote: ", trial, judge, user, vote)
    configuration = gara.getConfiguration(connection)

    if trial != configuration['currentTrial']:
        abort(403, {'code': 1, 'error': 'Trial not accepted'})

    if not (0 <= user <= configuration['nUsers']):
        abort(403, {'code': 2, 'error': 'User not valid'})

    if not (0 <= vote <= 10.00):
        abort(403, {'code': 3, 'error': 'Vote not valid'})

    if not gara.validJudge(judge, ua):
        abort(403, {'code': 4, 'error': 'Judge not maching registered uuid'})

    response = gara.addRemoteVote(connection, trial, user, judge, vote)
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
        where = QStandardPaths.DocumentsLocation
        dd = QStandardPaths.writableLocation(where)

        filename = QFileDialog.getSaveFileName(self,
                                               _translate("MainWindow", "Salva come..."),
                                               dd,
                                               _translate("MainWindow", "File di gara (*.gara *.db)"))
        if filename:
            fn = filename[0]
            pn = pathlib.Path(fn)
            pn.unlink()
            gara = Gara(description=self.ui.description.text(),
                        nJudges=int(self.ui.numeroGiudici.currentText()),
                        date=self.ui.dateEdit.date(),
                        nTrials=int(self.ui.prove.currentText()),
                        nUsers=int(self.ui.atleti.text()),
                        filename=filename[0])
            gara.createDB()
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
        Gara.setActiveInstance(gara)
        assert gara == Gara.activeInstance, "not the same"
        self.connection = gara.getConnection()
        # gara is on a different thread but for Qt is the same
        gara.vote_updated.connect(self.voteUpdated, Qt.QueuedConnection)
        print("UI connection:", self.connection)
        self.updateUI()
        self.prepareModel(gara.getConfiguration(self.connection))

    @pyqtSlot(int, int, int, float)
    def voteUpdated(self, trial, user, judge, vote):
        print("Vote received by UI:", trial, user, judge, vote)
        item = self.model.item(user-1, judge)
        item.setText("{}".format(vote))
        item = self.model.item(user-1, 0)
        item.setText("{}".format(trial+1))

    def updateUI(self):
        gara = Gara.activeInstance
        if gara is None:
            self.setWindowTitle(_translate("MainWindow", "Giudice di gara v1.0 - non configurato"))
            return

        configuration = gara.getConfiguration(self.connection)

        self.setWindowTitle(_translate("MainWindow", "Giudice di gara v1.0 - {}".format(gara.filename)))
        self.ui.description.setText(configuration['description'])

        ntrials = "{}/{}".format(configuration['currentTrial']+1,
                                 configuration['nTrials'])
        self.ui.currentTrial.setText(ntrials)

        nusers = "{}/{}".format(0, configuration['nUsers'])
        self.ui.usersCounter.setText(nusers)

        stato = ""
        state_conn = _translate("MainWindow", "Connesso")
        state_nconn = _translate("MainWindow", "Non connesso")

        for i in range(1, configuration['nJudges']+1):
            val = gara.usersUUID.get(i)
            if val is not None:
                state = state_conn
                lt = gara.usersTIME.get(val)
                diff = time.time() - lt
                if diff <= 3.0:
                    color = "green"
                elif diff <= 5.0:
                    color = "yellow"
                elif diff <= 10.0:
                    color = "orange"
                else:
                    color = "red"
                    state = state_nconn
                sg = '<font color=\"{}\">{}</font>'.format(color, state)
            else:
                sg = '<font color=\"red\">{}</font>'.format(state_nconn)
            stato += _translate("MainWindow", "Giudice {}: {}").format(i, sg)
            stato += " | "
        self.statusLabel.setText(stato)

    def prepareModel(self, configuration):
        cols = 1+configuration['nJudges']
        rows = configuration['nUsers']
        self.model = QStandardItemModel(rows, cols)

        labels = [_translate("MainWindow", "Prova")]
        for j in range(1, configuration['nJudges']+1):
            labels.append(_translate("MainWindow", "Giudice {}").format(j))

        self.model.setHorizontalHeaderLabels(labels)
        for y in range(0, rows):
            for x in range(0, cols):
                item = QStandardItem("")
                item.setEditable(False)
                item.setSelectable(True)
                self.model.setItem(y, x, item)
        self.ui.tableView.setModel(self.model)
        for i in range(0, len(self.ui.tableView.horizontalHeader())):
            self.ui.tableView.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

    def saveAs(self):
        where = QStandardPaths.DocumentsLocation
        dd = QStandardPaths.writableLocation(where)
        filename = QFileDialog.getSaveFileName(self,
                                               _translate("MainWindow", "Salva come..."),
                                               dd,
                                               _translate("MainWindow", "File di gara (*.gara *.db)"))
        if filename:
            Gara.activeInstance.saveAs(self.connection, filename[0])
            QMessageBox.information(self, "", _translate("MainWindow", "Copia creata"), QMessageBox.Ok)


    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionNuova_gara.triggered.connect(self.showNuovaGara)
        self.ui.actionSaveAs.triggered.connect(self.saveAs)
        self.showNuovaGara()
        self.statusLabel = QLabel(self.ui.statusbar)
        self.ui.statusbar.addPermanentWidget(self.statusLabel)
        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableView.setAlternatingRowColors(True)
        timer = QTimer(self)
        timer.timeout.connect(self.updateUI)
        timer.start(1000)

if __name__ == '__main__':
    # empty Gara
    gara = Gara()
    gara.createDB()
    Gara.setActiveInstance(gara)
    assert gara == Gara.activeInstance, "not set"
    assert gara.connection, "connection not set"

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
