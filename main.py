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

    if configuration['state'] != State_Running:
        abort(500, {'error': 'gara not configured yet'})

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
            'max': configuration['nJudges']})

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

    configuration = gara.getConfiguration(connection)

    if configuration['state'] != State_Running:
        abort(500, {'error': 'gara not configured yet'})

    print("Add vote: ", trial, judge, user, vote)

    if trial != configuration['currentTrial']:
        abort(403, {'code': 1, 'error': 'Trial not accepted'})

    if not (0 <= user <= configuration['nUsers']):
        abort(403, {'code': 2, 'error': 'User not valid'})

    if not (0 <= vote <= 100.00):
        abort(403, {'code': 3, 'error': 'Vote not valid'})

    if not gara.validJudge(judge, ua):
        abort(403, {'code': 4, 'error': 'Judge not maching registered uuid'})

    response = gara.addRemoteVote(connection, trial, user, judge, vote)
    if response.get('error'):
        abort(403, response)

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
        self.ui.numeroGiudici.setCurrentIndex(5)
        self.ui.prove.setCurrentIndex(3)
        self.ui.radioButton.setChecked(True)

    def accept(self):
        ng = int(self.ui.numeroGiudici.currentText())
        if self.ui.radioButton_2.isChecked() and ng <= 3:
            testo = _translate("MainWindow", "La media mediata richiede almeno 4 giudici")
            dlg = QMessageBox.information(self, "Attenzione",
                                          testo,
                                          QMessageBox.Ok)
            return

        average = Average_Aritmetica if self.ui.radioButton.isChecked() else Average_Mediata

        where = QStandardPaths.DocumentsLocation
        dd = QStandardPaths.writableLocation(where)

        filename = QFileDialog.getSaveFileName(self,
                                               _translate("MainWindow", "Salva come..."),
                                               dd,
                                               _translate("MainWindow", "File di gara (*.gara *.db)"))
        if filename != None and filename[0] != '':
            fn = filename[0]
            pn = pathlib.Path(fn)
            if pn.exists():
                pn.unlink()
            gara = Gara(description=self.ui.description.text(),
                        nJudges=int(ng),
                        date=self.ui.dateEdit.date(),
                        nTrials=int(self.ui.prove.currentText()),
                        nUsers=int(self.ui.atleti.text()),
                        average=average,
                        filename=filename[0])
            gara.createDB()
            self.parent().setGara(gara)
            super().accept()

    def reject(self):
        super().reject()


class DlgConfigCredits (QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = ui.Ui_DialogCredits()
        self.ui.setupUi(self)
        self.setModal(True)

        self.connection = Gara.activeInstance.getConnection()
        self.configuration = Gara.activeInstance.getConfiguration(self.connection)
        self.rows = self.configuration['nUsers']+1
        self.trials = self.configuration['nTrials']

        labels = [
            _translate("Credits", "Pettorina"),
            _translate("Credits", "Nome e cognome")]
        for i in range(0, self.trials):
            labels.append(_translate("Credits", "Crediti\nProva {}".format(i+1)))

        self.cols = len(labels)
        self.model = QStandardItemModel(self.rows, self.cols)
        self.model.setHorizontalHeaderLabels(labels)

        self.ui.tableView.setModel(self.model)
        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableView.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.tableView.setAlternatingRowColors(True)
        self.ui.tableView.verticalHeader().setVisible(False)

        self.changes = {}

        for h in range(1, len(self.ui.tableView.horizontalHeader())):
            self.ui.tableView.horizontalHeader().setSectionResizeMode(h, QHeaderView.Stretch)

        for y in range(0, self.rows):
            user = Gara.activeInstance.getUserInfo(self.connection, y)
            for x in range(0, self.cols):
                item = QStandardItem("")
                item.setSelectable(True)
                self.model.setItem(y, x, item)
                if x == 0:
                    item.setEditable(False)
                    g = item.font()
                    g.setBold(True)
                    item.setFont(g)
                    # b = QBrush(QColor(200, 200, 200))
                    # item.setBackground(b)
                    item.setText(str(y))
                if x == 1:
                    item.setData({'check': 'str', 'user': y, 'col': x-1})
                    if user:
                        v = user['nickname']
                        if v is not None:
                            item.setText(v)
                if x > 1:
                    item.setData({'check': 'float', 'user': y, 'col': x-1})
                    if user:
                        v = user['credits'][x-2]
                        if v is not None:
                            item.setText(str(v))

        self.model.itemChanged.connect(self.itemChanged)

    @pyqtSlot(QStandardItem)
    def itemChanged(self, item):
        data = item.data()
        if data is not None:
            user = data['user']
            col = data['col']
            if data['check'] == 'str':
                v = item.text().strip()
            if data['check'] == 'float':
                try:
                    v = float(item.text())
                except ValueError:
                    v = 0.0
            item.setText(str(v))
            g = self.changes.get(user, {})
            g[col] = v
            self.changes[user] = g

    def accept(self):
        Gara.activeInstance.updateUserInfo(self.connection, self.changes)
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
        gara.vote_deleted.connect(self.voteDeleted, Qt.QueuedConnection)
        print("UI connection:", self.connection)
        self.updateUI()
        self.prepareModel()

    @pyqtSlot(int, int, int, float)
    def voteUpdated(self, trial, user, judge, vote):
        print("Vote received by UI:", trial, user, judge, vote)
        table = self.tables[trial]
        configuration = Gara.activeInstance.getConfiguration(self.connection)
        user_data = Gara.activeInstance.getUser(self.connection, user)
        model = self.tables[trial].model()
        self.updateTableRow(table, trial, user, configuration, user_data)

    @pyqtSlot()
    def updateUI(self):
        gara = Gara.activeInstance
        mainbuttons = [self.ui.nextTrialButton, self.ui.endButton, self.ui.startButton]

        for btn in mainbuttons:
            btn.setEnabled(gara is not None)

        if gara is None:
            self.deselect()
            self.setWindowTitle(_translate("MainWindow", "Giudice di gara v1.0 - non configurato"))
            return

        configuration = gara.getConfiguration(self.connection)
        trial = configuration['currentTrial']
        nt = configuration['nTrials']

        self.setWindowTitle(_translate("MainWindow", "Giudice di gara v1.0 - {} (autosalvataggio)".format(gara.filename)))
        self.ui.description.setText(configuration['description'])
        self.ui.nextTrialButton.setEnabled(trial+1 < nt and configuration['state'] == State_Running)
        self.ui.startButton.setEnabled(configuration['state'] == State_Configure)
        self.ui.endButton.setEnabled(configuration['state'] == State_Running)

        medie = {
            Average_Aritmetica: _translate("MainWindow", "aritmetica"),
            Average_Mediata: _translate("MainWindow", "mediata"),
        }
        self.ui.average.setText(medie[configuration['average']])

        ntrials = "{}/{}".format(trial+1, nt)
        self.ui.currentTrial.setText(ntrials)

        done = gara.activeInstance.countDone(self.connection, trial)
        nusers = "{}/{}".format(done, configuration['nUsers'])
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

    def createTableAndModel(self, rows, cols, labels):
        tv = QTableView(self)
        model = QStandardItemModel(rows, cols)
        model.setHorizontalHeaderLabels(labels)

        tv.setModel(model)
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        tv.setSelectionMode(QAbstractItemView.SingleSelection)
        tv.setAlternatingRowColors(True)
        tv.verticalHeader().setVisible(False)

        for h in range(0, len(tv.horizontalHeader())):
            tv.horizontalHeader().setSectionResizeMode(h, QHeaderView.Stretch)

        m = tv.selectionModel()
        m.currentRowChanged.connect(lambda a, b, table=tv: self.selection(a, b, table))
        return (tv, model)

    def prepareModel(self):
        gara = Gara.activeInstance
        configuration = gara.getConfiguration(self.connection)

        cols = configuration['nJudges'] + 2
        rows = configuration['nUsers']
        trials = configuration['nTrials']

        labels = [_translate("MainWindow", "Pettorina")]
        for j in range(1, configuration['nJudges']+1):
            labels.append(_translate("MainWindow", "Giudice {}").format(j))
        labels.append(_translate("MainWindow", "Punteggio\nprova"))
        tables = []
        models = []

        self.ui.tabWidget.clear()
        for i in range(trials):
            tv, model = self.createTableAndModel(rows, cols, labels)
            tables.append(tv)
            models.append(model)
            self.ui.tabWidget.addTab(tv, _translate("MainWindow", "Prova {}".format(i+1)))

        for y in range(0, rows+1):
            user = gara.getUser(self.connection, y)
            for trial in range(0, trials):
                for x in range(0, cols):
                    item = QStandardItem("")
                    item.setEditable(False)
                    item.setSelectable(True)
                    models[trial].setItem(y, x, item)
                self.updateTableRow(tables[trial], trial, y, configuration, user)

        self.tables = tables
        self.createTableViewFromResults()
        self.deselect()

    def createTableViewFromResults(self):
        gara = Gara.activeInstance
        configuration = gara.getConfiguration(self.connection)

        rows = configuration['nUsers']
        trials = configuration['nTrials']

        labels = [_translate("MainWindow", "Pettorina")]
        for j in range(0, trials):
            labels.append(_translate("MainWindow", "Punteggio\nprova {}").format(j+1))
        labels.append(_translate("MainWindow", "Media"))
        labels.append(_translate("MainWindow", "Punteggio\ncon credito"))
        labels.append(_translate("MainWindow", "Somma"))
        cols = len(labels)
        tv, model = self.createTableAndModel(rows, cols, labels)
        self.tables.append(tv)
        for y in range(0, rows+1):
            for x in range(0, cols):
                item = QStandardItem("")
                item.setEditable(False)
                item.setSelectable(True)
                model.setItem(y, x, item)
            tv.hideRow(y)

        self.ui.tabWidget.addTab(tv, _translate("MainWindow", "Risultati"))

    def updateTableRow(self, table, trial, row, configuration, user):
        mostra = False
        model = table.model()
        votes = user['trials'][trial]['votes']
        cols = model.columnCount()
        for x in range(0, cols):
            item = model.item(row, x)
            # pettorina
            if x == 0:
                item.setText(str(row))
            # votes
            if x >= 1 and x <= configuration['nJudges']:
                if votes[x] is not None:
                    mostra = True
                    item.setText(str(votes[x]))
            # score
            if x == cols-1:
                score = user['trials'][trial]['score']
                if score is not None:
                    item.setText(str(score))
        if mostra:
            table.showRow(row)
        else:
            table.hideRow(row)

    def selection(self, a, b, table):
        if table == self.tables[-1]:
            # special Results causes, let's pretend its the latest trial
            self.selected_trial = self.tables.index(table) - 1
        else:
            self.selected_trial = self.tables.index(table)
        self.selected_user = a.row()

        user = Gara.activeInstance.getUser(self.connection, self.selected_user)
        configuration = Gara.activeInstance.getConfiguration(self.connection)

        mainbuttons = [self.ui.sendToDisplay, self.ui.deselectRow]
        for btn in mainbuttons:
            btn.setEnabled(True)

        self.ui.retryTrial.setEnabled(configuration['state'] == State_Running)

        self.ui.userNumber.setText(str(self.selected_user))
        self.ui.userTrial.setText(str(self.selected_trial+1))
        score = user['trials'][self.selected_trial]['score']
        self.ui.userTrialAverage.setText(str(score) if score != None else "")
        results = user.get('results')
        if results:
            self.ui.userAverageAll.setText(str(results['average']))
            self.ui.userAverageAllAndBonus.setText(str(results['average_bonus']))
            self.ui.userSum.setText(str(results['sum']))
        else:
            self.ui.userAverageAll.setText("")
            self.ui.userAverageAllAndBonus.setText("")
            self.ui.userSum.setText("")

    @pyqtSlot()
    def deselect(self):
        self.selected_user = None
        self.selected_trial = None

        for table in self.tables:
            m = table.selectionModel()
            if m:
                m.clear()

        mainbuttons = [self.ui.retryTrial, self.ui.sendToDisplay, self.ui.deselectRow]
        for btn in mainbuttons:
            btn.setEnabled(False)

        self.ui.userNumber.setText("")
        self.ui.userTrial.setText("")
        self.ui.userTrialAverage.setText("")
        self.ui.userAverageAll.setText("")
        self.ui.userAverageAllAndBonus.setText("")
        self.ui.userSum.setText("")

    @pyqtSlot()
    def retryTrial(self):
        if self.selected_user is None or self.selected_trial is None:
            return

        testo = _translate("MainWindow", "Tutti i giudizi per la pettorina {} della prova {} verranno eliminati. Vuoi proseguire ?").format(self.selected_user, self.selected_trial+1)
        dlg = QMessageBox.question(self, "Attenzione",
                                   testo,
                                   QMessageBox.Yes | QMessageBox.No)
        if dlg == QMessageBox.Yes:
            Gara.activeInstance.deleteTrialForUser(self.connection, self.selected_trial, self.selected_user)

    @pyqtSlot(int, int)
    def voteDeleted(self, trial, user):
        table = self.tables[trial]
        model = table.model()
        for i in range(1, model.columnCount()):
            item = model.item(user, i)
            item.setText("")

    @pyqtSlot()
    def saveAs(self):
        if Gara.activeInstance is None:
            return
        where = QStandardPaths.DocumentsLocation
        dd = QStandardPaths.writableLocation(where)
        filename = QFileDialog.getSaveFileName(self,
                                               _translate("MainWindow", "Salva come..."),
                                               dd,
                                               _translate("MainWindow", "File di gara (*.gara *.db)"))

        if filename != None and filename[0] != '':
            Gara.activeInstance.saveAs(self.connection, filename[0])
            QMessageBox.information(self, "", _translate("MainWindow", "Copia creata"), QMessageBox.Ok)


    @pyqtSlot()
    def open(self):
        if Gara.activeInstance is not None:
            res = QMessageBox.warning(self,
                                      _translate("MainWindow", "Attenzione"),
                                      _translate("MainWindow", "La gara corrente verra' chiusa.\nVuoi continuare?"),
                                      QMessageBox.Yes | QMessageBox.No)
        else:
            res = QMessageBox.Yes

        if res == QMessageBox.Yes:
            where = QStandardPaths.DocumentsLocation
            dd = QStandardPaths.writableLocation(where)
            filename = QFileDialog.getOpenFileName(self,
                                                   _translate("MainWindow", "Apri gara..."),
                                                   dd,
                                                   _translate("MainWindow", "File di gara (*.gara *.db)"))
            if filename != None and filename[0] != '':
                try:
                    gara = Gara.fromFilename(filename[0])
                except:
                    QMessageBox.critical(self,
                                         _translate("MainWindow", "Errore"),
                                         _translate("MainWindow", "Il file scelto non rappresenta un formato di gara valido"),
                                         QMessageBox.Ok)
                else:
                    self.setGara(gara)

    @pyqtSlot()
    def nextTrial(self):
        dlg = QMessageBox.information(self,
                                      _translate("MainWindow", "Attenzione"),
                                      _translate("MainWindow", "Avanzando di prova non sara' piu' possibile registrare voti per le prove precedenti. Proseguire ?"),
                                      QMessageBox.Yes | QMessageBox.No)
        if dlg == QMessageBox.Yes:
            ok, trial = Gara.activeInstance.advanceToNextTrial(self.connection)
            if ok:
                self.ui.tabWidget.setCurrentIndex(trial)

    @pyqtSlot(int)
    def tabbarChanged(self, index):
        self.deselect()

    @pyqtSlot()
    def start(self):
        dlg = QMessageBox.information(self,
                                      _translate("MainWindow", "Attenzione"),
                                      _translate("MainWindow", "Avviando la gara non sara' piu' possibile impostare i crediti. Proseguire ?"),
                                      QMessageBox.Yes | QMessageBox.No)
        if dlg == QMessageBox.Yes:
            Gara.activeInstance.setState(self.connection, State_Running)

    @pyqtSlot()
    def end(self):
        dlg = QMessageBox.information(self,
                                      _translate("MainWindow", "Attenzione"),
                                      _translate("MainWindow", "Fermando la gara non saranno accettati piu' dati in ingresso e la gara verra' considerata conclusa allo stato attuale. Proseguire ?"),
                                      QMessageBox.Yes | QMessageBox.No)
        if dlg == QMessageBox.Yes:
            Gara.activeInstance.setState(self.connection, State_Completed)
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count()-1)
            self.deselect()
            self.fillTableWithResults(self.tables[-1])

    def fillTableWithResults(self, table):
        model = table.model()
        configuration = Gara.activeInstance.getConfiguration(self.connection)
        rows = configuration['nUsers']
        for row in range(0, rows+1):
            user = Gara.activeInstance.getUser(self.connection, row)
            results = user.get('results')
            if results:
                vals = []
                vals.append(str(row))
                for trial in range(0, configuration['nTrials']):
                    score = user['trials'][trial]['score']
                    vals.append(str(score))
                vals.append(str(results['average']))
                vals.append(str(results['average_bonus']))
                vals.append(str(results['sum']))
                cols = model.columnCount()
                for x in range(0, cols):
                    item = model.item(row, x)
                    item.setText(vals[x])
                table.showRow(row)
            else:
                table.hideRow(row)

    def configuraPettorine(self):
        configuration = Gara.activeInstance.getConfiguration(self.connection)
        if configuration['state'] == State_Configure:
            dlg = DlgConfigCredits(self)
            dlg.show()
        else:
            dlg = QMessageBox.information(self,
                                          _translate("MainWindow", "Attenzione"),
                                          _translate("MainWindow", "A gara avviata non e' possibile modificare i bonus."),
                                          QMessageBox.Ok)


    def __init__(self):
        QMainWindow.__init__(self)
        self.tables = []
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionNuova_gara.triggered.connect(self.showNuovaGara)
        self.ui.actionSaveAs.triggered.connect(self.saveAs)
        self.ui.actionCarica.triggered.connect(self.open)
        self.ui.actionPettorine.triggered.connect(self.configuraPettorine)
        self.showNuovaGara()
        self.statusLabel = QLabel(self.ui.statusbar)
        self.ui.statusbar.addPermanentWidget(self.statusLabel)
        self.ui.deselectRow.released.connect(self.deselect)
        self.ui.retryTrial.released.connect(self.retryTrial)
        self.ui.nextTrialButton.released.connect(self.nextTrial)
        self.ui.tabWidget.currentChanged.connect(self.tabbarChanged)
        self.ui.startButton.released.connect(self.start)
        self.ui.endButton.released.connect(self.end)

        timer = QTimer(self)
        timer.timeout.connect(self.updateUI)
        timer.start(1000)

if __name__ == '__main__':
    debug = True
    if debug:
        # empty Gara
        # gara = Gara(nJudges=2, nUsers=2, nTrials=2)
        # gara.createDB()
        gara = Gara.fromFilename("/Users/nferruzzi/Documents/semplice.gara")
        Gara.setActiveInstance(gara)
        resetToTrial(gara.getConnection(), 0)
        setState(gara.getConnection(), State_Configure)
        assert gara == Gara.activeInstance, "not set"
        assert gara.connection, "connection not set"

    # webservice
    controller = Controller()
    tr = threading.Thread(target=controller.listen)
    tr.start()

    # main ui
    app = QApplication(sys.argv)
    MainWindow = GaraMainWindow()
    if debug:
        MainWindow.setGara(gara)
    MainWindow.show()
    v = app.exec_()

    # shutdown
    controller.shutdown()
    sys.exit(v)
