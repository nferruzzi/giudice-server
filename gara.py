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
MAX_JUDGES = 6
MAX_TRIALS = 10

Average_Aritmetica = 0
Average_Mediata = 1

State_Configure = 0
State_Running = 1
State_Completed = 2


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
"average" INTEGER,
"state" INTEGER,
"uuid" VARCHAR(250),
PRIMARY KEY (id)
);
CREATE TABLE credits (
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
nickname VARCHAR(250),
PRIMARY KEY (user)
);
PRAGMA user_version={};
""".format(USER_DB_VERSION)
    connection.cursor().execute(cmd)


def getUserInfo(connection, user):
    query = 'select * from credits where user=?'
    for v in connection.cursor().execute(query, (user,)):
        vals = v[1:11]
        vals = list(map(lambda x: 0.0 if x is None else x, vals))
        return {
            'nickname': v[11],
            'credits': vals
        }
    return {
        'nickname': '',
        'credits': [0.0, ]*10
    }


def updateUserInfo(connection, user, payload):
    print("Payloads:", payload)
    with connection:
        cols = []
        vals = []
        ques = []
        vks = []
        n = payload.get(0)
        if n is not None:
            cols.append('nickname')
            vals.append(n)
            ques.append('?')
            vks.append('nickname=?')
        for i in range(1, MAX_TRIALS+1):
            c = payload.get(i)
            if c:
                e = 'trial{}'.format(i)
                cols.append(e)
                vals.append(c)
                ques.append('?')
                vks.append('{}=?'.format(e))

        query = 'select * from credits where user=?'
        cursor = connection.cursor()
        update = False
        for values in cursor.execute(query, (user,)):
            update = True
            break

        if update:
            vk = ", ".join(vks)
            print(vk)
            query = 'update credits set {} where user=?'.format(vk)
            vals.append(user)
            print("Update credits: ", query, vals)
            cursor.execute(query, vals)
        else:
            cols.append('user')
            vals.append(user)
            ques.append('?')
            cn = ", ".join(cols)
            vn = ", ".join(ques)
            query = 'insert into credits ({}) values ({})'.format(cn, vn)
            cursor.execute(query, vals)
            print("New credits:", query, vals)


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
              description, date, nJudges, nUsers, nTrials, average, state, uuid):
    assert isinstance(date, datetime.date)
    # we want just one conf
    vals = (1, description, dateToSQLite(date), nJudges, nUsers, nTrials, 0, average, state, uuid)
    connection.cursor().execute('insert into config (id, description, date, "nJudges", "nUsers", "nTrials", "currentTrial", average, state, uuid) values(?,?,?,?,?,?,?,?,?,?)', vals)


def advanceToNextTrial(connection):
    config = getConfig(connection)
    trial = config['currentTrial'] + 1
    if trial >= config['nTrials']:
        return (False, trial)
    query = 'update config set "currentTrial"=? where id=1'
    connection.cursor().execute(query, (trial,))
    return (True, trial)


def resetToTrial(connection, trial=0):
    query = 'update config set "currentTrial"=? where id=1'
    connection.cursor().execute(query, (trial,))


def setState(connection, state=State_Configure):
    query = 'update config set "state"=? where id=1'
    connection.cursor().execute(query, (state,))


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
            'average': v[7],
            'state': v[8],
            'uuid': v[8],
        }
    return None


def addVote(connection, trial, user, judge, vote):
    assert judge > 0, "judge starts from 1"
    query = 'select * from users where user=? and trial=?'
    trovato = None
    vf = 'vote{}'.format(judge)
    for v in connection.cursor().execute(query, (user, trial)):
        trovato = v
    if not trovato:
        print("Insert vote")
        query = 'insert into users (trial, user, {}) values(?, ?, ?)'.format(vf)
        connection.cursor().execute(query, (trial, user, vote))
    else:
        # update
        print("Update vote")
        current = v[2+judge]
        if current is not None:
            print("Duplicated vote for user {} judge {}".format(user, judge))
            return False
        query = 'update users set "{}"=? where id=?'.format(vf)
        connection.cursor().execute(query, (vote, v[0]))
    return True


def getUser(connection, user):
    conf = getConfig(connection)
    nj = conf['nJudges']
    nt = conf['nTrials']
    average = conf['average']
    query = 'select trial, vote1, vote2, vote3, vote4, vote5, vote6 from users where user=?'
    response = {}
    trials = {}

    # get credits, they are used one by one or all together
    credits = getUserInfo(connection, user)
    sum_credits = sum(credits['credits'])

    for vals in connection.cursor().execute(query, (user,)):
        t = vals[0]
        # judge votes are stored from 1:..
        vt = vals[1:]
        votes = {
            1: vt[0],
            2: vt[1],
            3: vt[2],
            4: vt[3],
            5: vt[4],
            6: vt[5],
        }

        # we remove votes not needed so we can test for None properly
        for i in range(nj+1, MAX_JUDGES+1):
            del votes[i]

        trials[t] = {}
        trials[t]['votes'] = votes

        if None in votes.values():
            score = None
            score_bonus = None
        else:
            vt = votes.values()
            if average == Average_Aritmetica:
                score = sum(vt) / len(vt)
            else:
                score = (sum(vt) - min(vt) - max(vt)) / (len(vt)-2)
            score = float("{:0.2f}".format(score))
            # each trial has its own bonus
            trial_credit = credits['credits'][t]
            score_bonus = score + trial_credit

        trials[t]['score'] = score
        trials[t]['score_bonus'] = score_bonus

    if len(trials) == nt:
        # we have all data needed to calc the results
        finals = list(map(lambda x: x['score'], trials.values()))
        finals_average = list(map(lambda x: x['score_bonus'], trials.values()))

        if None not in finals:
            # average
            average = sum(finals) / len(finals)
            # average with bonus
            average_bonus = sum(finals_average) / len(finals_average)

            results = {}
            results['average'] = float("{:0.2f}".format(average))
            results['average_bonus'] = float("{:0.2f}".format(average_bonus))
            results['sum'] = float("{:0.2f}".format(sum(finals_average)))
            response['results'] = results
    else:
        # fill with dummy data
        for k in range(0, conf['nTrials']):
            if trials.get(k) == None:
                votes = {}
                for i in range(0, MAX_JUDGES):
                    votes[i+1] = None
                trials[k] = {}
                trials[k]['votes'] = votes
                trials[k]['score'] = None
                trials[k]['score_bonus'] = None

    # we need them ordered to create progessive averages
    def calcProgressive(key, store):
        all_score = []
        for i in range(0, len(trials)):
            score = trials[i].get(key)
            if score is None:
                break
            all_score.append(score)
            avg = sum(all_score) / len(all_score)
            trials[i][store] = float("{:0.2f}".format(avg))

    calcProgressive('score', 'average')
    calcProgressive('score_bonus', 'average_bonus')
    response['trials'] = trials

    return response


def deleteTrialForUser(connection, trial, user):
    query = 'delete from users where "user"=? AND "trial"=?'
    connection.cursor().execute(query, (user, trial))


def countDone(connection, trial):
    configuration = getConfig(connection)
    query = 'select count(*) from users where "trial"=? AND'
    mv = []
    for i in range(1, configuration['nJudges']+1):
        mv.append('"vote{}" is not NULL'.format(i))
    query += ' AND '.join(mv)
    query += ';'
    for v in connection.cursor().execute(query, (trial,)):
        return v[0]
    return 0


class Gara(QObject):

    DONOT_ALLOW_DUPLICATE_JUDGES = True
    activeInstance = None
    lock = threading.RLock()

    # signal (trial, user, judge, vote)
    vote_updated = pyqtSignal(int, int, int, float, name='voteUpdated')
    # signal (trial, user)
    vote_deleted = pyqtSignal(int, int, name='voteDeleted')

    def __init__(self,
                 description="Non configurata",
                 nJudges=6,
                 date=None,
                 nTrials=3,
                 nUsers=5,
                 filename=None,
                 average=Average_Aritmetica):
        super(QObject, self).__init__()
        self._description = description
        self._nJudges = nJudges
        self._date = date if date is not None else QDate.currentDate()
        self._nTrials = nTrials
        self._nUsers = nUsers
        self._average = average
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
    def fromFilename(filename):
        gara = Gara(filename=filename)
        gara.openDB()
        return gara

    @staticmethod
    def setActiveInstance(gara):
        assert gara.connection, "connection not available"
        with Gara.lock:
            Gara.activeInstance = gara
            print("Set active instance: ", gara)

    def getConnection(self):
        with self.lock:
            return apsw.Connection(str(self.filename))

    def openDB(self):
        with self.lock:
            self.connection = self.getConnection()
            if checkDBVersion(self.connection) != USER_DB_VERSION:
                raise Exception("DB not compatible")
            self._created = True

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
                          average=self._average,
                          state=State_Configure,
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

    def registerJudgeWithUUID(self, connection, judge, uuid):
        with self.lock:
            configuration = self.getConfiguration(connection)
            if judge <= 0 or judge > configuration['nJudges']:
                # should be 409 but QML XHTTPXmlRequest.status is bugged on
                # android and return 0
                return (404, {
                    'error': 'judge not in range',
                    'max': configuration['nJudges']
                })

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
            if present != uuid:
                return (403, {'error': 'judge in use'})
            return (200, {})

    def validJudge(self, judge, uuid):
        with self.lock:
            v = self.usersUUID.get(judge)
            if v is None:
                return False
            return v == uuid

    def addRemoteVote(self, connection, trial, user, judge, user_uuid, vote):
        with self.lock:
            configuration = self.getConfiguration(connection)

            if configuration['state'] != State_Running:
                return (500, {'code': 0, 'error': 'gara not configured yet'})

            if trial != configuration['currentTrial']:
                return (403, {'code': 1, 'error': 'Trial not accepted'})

            if not (0 <= user <= configuration['nUsers']):
                return (403, {'code': 2, 'error': 'User not valid'})

            if not (0 <= vote <= 100.00):
                return (403, {'code': 3, 'error': 'Vote not valid'})

            if not self.validJudge(judge, user_uuid):
                return (403, {'code': 4, 'error': 'Judge not maching registered uuid'})

            print("Add vote: ", trial, judge, user, vote)
            v = addVote(connection,
                        trial=trial,
                        user=user,
                        judge=judge,
                        vote=vote)
            if v:
                self.vote_updated.emit(trial, user, judge, vote)
                return (200, {})

            return (403, {'code': 5, 'error': 'duplicate'})

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

    def getUser(self, connection, user):
        with self.lock:
            return getUser(connection, user)

    def deleteTrialForUser(self, connection, trial, user):
        print("Delete user {} trial {}".format(user, trial))
        with self.lock:
            deleteTrialForUser(connection, trial, user)
            self.vote_deleted.emit(trial, user)

    def countDone(self, connection, trial):
        with self.lock:
            return countDone(connection, trial)

    def advanceToNextTrial(self, connection):
        with self.lock:
            return advanceToNextTrial(connection)

    def setState(self, connection, state=State_Configure):
        with self.lock:
            return setState(connection, state)

    def updateUserInfo(self, connection, payloads):
        with self.lock:
            for k, v in payloads.items():
                updateUserInfo(connection, k, v)

    def getUserInfo(self, connection, user):
        with self.lock:
            return getUserInfo(connection, user)


if __name__ == '__main__':
    c = apsw.Connection(":memory:")
    if checkDBVersion(c) != USER_DB_VERSION:
        print("Creating")
        createTableV2(c)
        today = datetime.date.today()
        setConfig(c, "test", today, 6, 100, 3, 0, 0, "uuid")
    print(getConfig(c))
    addVote(c, 0, 1, 1, 6.0)
    addVote(c, 0, 1, 2, 9.0)
    addVote(c, 0, 1, 1, 9.0)
    updateUserInfo(c, 0, {0: 'nf', 1: 1.0, 2: 2.0})
    #updateUserInfo(c, 1, {1: 0.4, 2: 0.01})
    updateUserInfo(c, 0, {0: 'nf', 1: 1.0, 2: 2.0})
    updateUserInfo(c, 0, {0: ''})
    #updateUserInfo(c, 1, {1: 0.4, 2: 0.01})
    g = Gara()
    g.createDB()
    g.addRemoteVote(g.connection, trial=0, user=1, judge=4, vote=6.5)
    print(g.getState(g.connection))
