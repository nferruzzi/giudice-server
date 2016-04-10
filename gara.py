#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: MIT (see LICENSE)
"""
from PyQt5.QtCore import *
import datetime
import time
import threading
import pathlib
import apsw


USER_DB_VERSION = 2


def createTableV2(connection):
    cmd = """CREATE TABLE users (
id INTEGER NOT NULL,
user INTEGER NOT NULL,
trial INTEGER,
vote1 FLOAT,
vote2 FLOAT,
vote3 FLOAT,
vote4 FLOAT,
vote5 FLOAT,
vote6 FLOAT,
extra INTEGER,
PRIMARY KEY (id)
);
CREATE TABLE config (
id INTEGER NOT NULL,
description VARCHAR(250),
date DATE,
"nJudges" INTEGER,
"nUsers" INTEGER,
"nTrials" INTEGER,
"currentTrial" INTEGER,
uuid VARCHAR(250),
PRIMARY KEY (id)
);
CREATE TABLE bonus (
user INTEGER NOT NULL,
trial1 FLOAT,
trial2 FLOAT,
trial3 FLOAT,
trial4 FLOAT,
trial5 FLOAT,
trial6 FLOAT,
trial7 FLOAT,
trial8 FLOAT,
trial9 FLOAT,
trial10 FLOAT,
PRIMARY KEY (user)
);
PRAGMA user_version={};
""".format(USER_DB_VERSION)
    connection.cursor().execute(cmd)


def checkDBVersion(connection):
    for v, in connection.cursor().execute('PRAGMA user_version'):
        return v
    return None


def dateToSQLite(d):
    return d.strftime('%Y-%m-%d')


def dateFromSQLite(column):
    s = column.split('-')
    year = int(s[0])
    month = int(s[1])
    day = int(s[2])
    return datetime.date(year=year, month=month, day=day)


def setConfig(connection,
              description, date, nJudges, nUsers, nTrials, uuid):
    assert isinstance(date, datetime.date)
    # we want just one conf
    vals = (1, description, dateToSQLite(date), nJudges, nUsers, nTrials, 0, uuid)
    connection.cursor().execute('insert into config (id, description, date, "nJudges", "nUsers", "nTrials", "currentTrial", uuid) values(?,?,?,?,?,?,?,?)', vals)


def getConfig(connection):
    query = "select * from config limit 1"
    for v in connection.cursor().execute(query):
        return {
            'description': v[1],
            'date': dateFromSQLite(v[2]),
            'nJudges': v[3],
            'nUsers': v[4],
            'nTrials': v[5],
            'currentTrial': v[6],
            'uuid': v[7],
        }
    return None


def addVote(connection, trial, user, judge, vote):
    query = 'select * from users where user=? and trial=?'
    trovato = None
    vf = 'vote{}'.format(judge)
    for v in connection.cursor().execute(query, (user, trial)):
        trovato = v
    if not trovato:
        # insert
        query = 'insert into users (trial, user, {}) values(?, ?, ?)'.format(vf)
        connection.cursor().execute(query, (trial, user, vote))
    else:
        # update
        query = 'update users set "{}"=? where id=?'.format(vf)
        print(query, v)
        connection.cursor().execute(query, (vote, v[0]))
    return True


class Gara(QObject):

    DONOT_ALLOW_DUPLICATE_JUDGES = True
    activeInstance = None
    lock = threading.RLock()

    # signal (trial, user, judge, vote)
    vote_updated = pyqtSignal(int, int, int, float, name='voteUpdated')

    def __init__(self,
                 description="Non configurata",
                 nJudges=6,
                 date=None,
                 nTrials=3,
                 nUsers=5,
                 filename=None):
        super(QObject, self).__init__()
        self._description = description
        self._nJudges = nJudges
        self._date = date if date is not None else QDate.currentDate()
        self._nTrials = nTrials
        self._nUsers = nUsers
        self._uuid = QUuid.createUuid().toString()
        self.usersUUID = dict()
        self.usersTIME = dict()
        self._created = False
        if filename:
            self.filename = pathlib.Path(filename)
        else:
            where = QStandardPaths.TempLocation
            dd = QStandardPaths.writableLocation(where)
            pd = pathlib.Path(dd)
            pu = pathlib.Path(self._uuid + '.gara')
            self.filename = pd / pu

    @staticmethod
    def setActiveInstance(gara):
        assert gara.connection, "connection not available"
        with Gara.lock:
            Gara.activeInstance = gara
            print("Set active instance: ", gara)

    def getConnection(self):
        return apsw.Connection(str(self.filename))

    def createDB(self):
        assert not self._created, "already created"
        with self.lock:
            self.connection = self.getConnection()

            if checkDBVersion(self.connection) == USER_DB_VERSION:
                raise Exception("DB found on same location")

            with self.connection:
                createTableV2(self.connection)
                setConfig(self.connection,
                          description=self._description,
                          date=datetime.date(year=self._date.year(),
                                             month=self._date.month(),
                                             day=self._date.day()),
                          nJudges=self._nJudges,
                          nUsers=self._nUsers,
                          nTrials=self._nTrials,
                          uuid=self._uuid)
                self._created = True

    def getConfiguration(self, connection):
        with self.lock:
            return getConfig(connection)

    def getState(self, connection):
        with self.lock:
            configuration = self.getConfiguration(connection)
            state = {
                "current_trial": configuration['currentTrial'],
                "max_trial": configuration['nTrials'],
                "latest_user": 0,
                "max_user": configuration['nUsers'],
                "uuid": configuration['uuid'],
                "description": configuration['description'],
            }
            return state

    def registerJudgeWithUUID(self, judge, uuid):
        with self.lock:
            if self.DONOT_ALLOW_DUPLICATE_JUDGES:
                # remove any judge with the same uuid
                for k, v in list(self.usersUUID.items()):
                    if v == uuid and k != judge:
                        print("Removed judge: {}".format(k))
                        del self.usersUUID[k]

                # register user
                present = self.usersUUID.get(judge)
                if present is None:
                    present = uuid
                    print("Add judge: {} -> {}".format(judge, present))
                    self.usersUUID[judge] = present
                else:
                    if present != uuid:
                        print("Judge conflict: {} -> {}")
            else:
                present = self.usersUUID.get(judge)
                if present != uuid:
                    print("Judgle conflict detected")
                present = uuid
                self.usersUUID[judge] = uuid

            self.usersTIME[uuid] = time.time()
            return present != uuid

    def validJudge(self, judge, uuid):
        with self.lock:
            v = self.usersUUID.get(judge)
            if v is None:
                return False
            return v == uuid

    def addRemoteVote(self, connection, trial, user, judge, vote):
        with self.lock:
            v = addVote(connection,
                        trial=trial,
                        user=user,
                        judge=judge,
                        vote=vote)
            if v:
                self.vote_updated.emit(trial, user, judge, vote)
                return True
            return False

    def save(self, connection, filename):
        self.properName = filename
        self._uuid = filename

    def saveAs(self, connection, filename):
        with self.lock:
            print("Saving as:", filename)
            db = apsw.Connection(filename)
            with db.backup("main", connection, "main") as b:
                while not b.done:
                    b.step(100)
                    print(b.remaining, b.pagecount, "\r")
            print("Saved.")


if __name__ == '__main__':
    c = apsw.Connection("pippo.db")
    if checkDBVersion(c) != USER_DB_VERSION:
        print("Creating")
        createTableV2(c)
        today = datetime.date.today()
        setConfig(cur, "test", today, 6, 100, 3, "uuid")
    print(getConfig(c))
    addVote(c, 0, 1, 1, 6.0)
    addVote(c, 0, 1, 2, 9.0)
    addVote(c, 0, 1, 3, 9.0)
    g = Gara()
    g.createDB()
    g.addRemoteVote(g.connection, trial=0, user=1, judge=4, vote=6.5)
    print(g.getState(g.connection))
