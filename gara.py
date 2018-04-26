#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: GPLv3 (see LICENSE)
"""
from PyQt5.QtCore import *
import datetime
import time
import threading
import pathlib
import apsw
import csv
from rapport import generateRapport

USER_DB_VERSION = 3
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
"maxVote" FLOAT,
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

def version_from_2_to_3(connection):
    cmd = """ALTER TABLE config ADD COLUMN "maxVote" FLOAT DEFAULT 100.0;
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
    with connection:
        cols = []
        vals = []
        ques = []
        vks = []
        n = payload.get(-1)
        if n is not None:
            cols.append('nickname')
            vals.append(n)
            ques.append('?')
            vks.append('nickname=?')
        for i in range(0, MAX_TRIALS):
            c = payload.get(i)
            if c is not None:
                e = 'trial{}'.format(i+1)
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
            query = 'update credits set {} where user=?'.format(vk)
            vals.append(user)
            # print("Update credits: ", query, vals)
            cursor.execute(query, vals)
        else:
            cols.append('user')
            vals.append(user)
            ques.append('?')
            cn = ", ".join(cols)
            vn = ", ".join(ques)
            query = 'insert into credits ({}) values ({})'.format(cn, vn)
            cursor.execute(query, vals)
            # print("New credits:", query, vals)


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
              description, date, nJudges, nUsers, nTrials, average, state, uuid, maxVote):
    assert isinstance(date, datetime.date)
    # we want just one conf
    vals = (1, description, dateToSQLite(date), nJudges, nUsers, nTrials, 0, average, state, uuid, maxVote)
    connection.cursor().execute('insert into config (id, description, date, "nJudges", "nUsers", "nTrials", "currentTrial", average, state, uuid, maxVote) values(?,?,?,?,?,?,?,?,?,?,?)', vals)


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


def resetMaxTrials(connection, trials=0):
    query = 'update config set "nTrials"=? where id=1'
    connection.cursor().execute(query, (trials,))


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
            'uuid': v[9],
            'maxVote': v[10],
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
    query = 'select trial, vote1, vote2, vote3, vote4, vote5, vote6 from users where user=? and trial<?'
    response = {}
    trials = {}

    # get credits, they are used one by one or all together
    credits = getUserInfo(connection, user)
    sum_credits = sum(credits['credits'])

    for vals in connection.cursor().execute(query, (user, nt)):
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

        score = None
        score_bonus = None
        partials = False

        if None in votes.values():
            # partial sums for the sake of it
            vt = list(votes.values())
            while None in vt:
                vt.remove(None)
            if len(vt):
                partials = True
                if average == Average_Aritmetica:
                    score = sum(vt) / len(vt)
                else:
                    if len(vt) > 2:
                        score = (sum(vt) - min(vt) - max(vt)) / (len(vt)-2)
        else:
            vt = votes.values()
            if average == Average_Aritmetica:
                score = sum(vt) / len(vt)
            else:
                score = (sum(vt) - min(vt) - max(vt)) / (len(vt)-2)

        if score is not None:
            # each trial has its own bonus
            trial_credit = credits['credits'][t]
            score_bonus = score + trial_credit

        trials[t]['score'] = score
        trials[t]['score_bonus'] = score_bonus
        trials[t]['average_bonus'] = None
        trials[t]['partials'] = partials
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
            results['average'] = average
            results['average_bonus'] = average_bonus
            results['sum'] = sum(finals_average)
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
                trials[k]['average'] = None
                trials[k]['average_bonus'] = None

    # we need them ordered to create progessive averages
    def calcProgressive(key, store):
        all_score = []
        for i in range(0, len(trials)):
            score = trials[i].get(key)
            if score is None:
                break
            all_score.append(score)
            avg = sum(all_score) / len(all_score)
            trials[i][store] = avg

    calcProgressive('score', 'average')
    calcProgressive('score_bonus', 'average_bonus')
    response['trials'] = trials

    return response


def deleteTrialForUser(connection, trial, user):
    query = 'delete from users where "user"=? AND "trial"=?'
    connection.cursor().execute(query, (user, trial))


def deleteTrialVotesForUser(connection, trial, user, judges):
    j = []
    for x in range(1, MAX_JUDGES+1):
        if x in judges:
            j.append('"vote{}"=null'.format(x))
    j = ", ".join(j)
    query = 'update users set {} where "user"=? AND "trial"=?'.format(j)
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


def countReceived(connection, trial):
    configuration = getConfig(connection)
    query = 'select count(*) from users where "trial"=? AND ('
    mv = []
    for i in range(1, configuration['nJudges']+1):
        mv.append('"vote{}" is not NULL'.format(i))
    query += ' OR '.join(mv)
    query += ');'
    for v in connection.cursor().execute(query, (trial,)):
        return v[0]
    return 0


def countIncomplete(connection, trial):
    configuration = getConfig(connection)
    mv = []
    query = 'select user, vote1, vote2, vote3, vote4, vote5, vote6 from users where "trial"=? AND ('
    for i in range(1, configuration['nJudges']+1):
        mv.append('"vote{}" is NULL'.format(i))
    query += ' OR '.join(mv)
    query += ');'
    res = []
    for v in connection.cursor().execute(query, (trial,)):
        if set(v[1:]) != set([None]):
            res.append(v[0])
    return res


def getAllUsersWithAVote(connection):
    query = 'select distinct user from users order by user asc;'
    res = []
    for v in connection.cursor().execute(query):
        res.append(v[0])
    return res


class TimeoutLock:
    lock = threading.RLock()

    def __enter__(self):
        # print(threading.currentThread().getName())
        return TimeoutLock.lock.acquire(timeout = 20.0)

    def __exit__(self, a, b, c):
        TimeoutLock.lock.release()

class Gara(QObject):

    DONOT_ALLOW_DUPLICATE_JUDGES = True
    activeInstance = None
    #lock = FakeLock() 
    #lock = threading.RLock()
    lock = TimeoutLock()

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
                 average=Average_Aritmetica, 
                 maxVote=100.0):
        super(QObject, self).__init__()
        self._description = description
        self._nJudges = nJudges
        self._date = date if date is not None else QDate.currentDate()
        self._nTrials = nTrials
        self._nUsers = nUsers
        self._average = average
        self._uuid = QUuid.createUuid().toString()
        self._maxVote = maxVote
        self.usersUUID = dict()
        self.usersTIME = dict()
        self._created = False
        self._message = None
        self._messageIndex = 0
        if filename:
            self.filename = pathlib.Path(filename)
        else:
            where = QStandardPaths.TempLocation
            dd = QStandardPaths.writableLocation(where)
            pd = pathlib.Path(dd)
            pu = pathlib.Path(self._uuid + '.gara')
            self.filename = pd / pu

    def close(self):
        with self.lock:
            self.connection = None
            Gara.activeInstance = None

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
            connection = apsw.Connection(str(self.filename))
            connection.setbusytimeout(15000)
            return connection

    def openDB(self):
        with self.lock:
            self.connection = self.getConnection()
            version = checkDBVersion(self.connection)
            if version != USER_DB_VERSION:
                # Let's BUMP
                if version == 2:
                    print("Bump DB from 2 to 3")
                    version_from_2_to_3(self.connection)
                    version = 3
                else:            
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
                          uuid=self._uuid,
                          maxVote=self._maxVote)
                self._created = True

    def getConfiguration(self, connection):
        with self.lock:
            return getConfig(connection)

    def getState(self, connection):
        with self.lock:
            configuration = self.getConfiguration(connection)
            msgs = {
                State_Running: "in corso",
                State_Completed: "terminato",
                State_Configure: "non iniziato",
            }
            date = configuration['date'].strftime('%d-%m-%Y')
            state = {
                "current_trial": configuration['currentTrial'],
                "max_trial": configuration['nTrials'],
                "latest_user": 0,
                "max_user": configuration['nUsers'],
                "uuid": configuration['uuid'],
                "description": configuration['description'],
                "state": msgs[configuration['state']],
                "date": date,
                "max_vote": configuration['maxVote']
            }
            if self._message is not None:
                state["message"] = {
                    "text": self._message,
                    "index": self._messageIndex
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

            if not (0 <= vote <= configuration['maxVote']):
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

    def getAllUsersWithAVote(self, connection):
        with self.lock:
            return getAllUsersWithAVote(connection)

    def generateRapport(self, connection, filename='demo2.xlsx', include=True):
        generateRapport(self, connection, filename, include)

    def setEnd(self, connection):
        with self.lock:
            conf = self.getConfiguration(connection)
            self.setState(connection, State_Completed)
            if conf['currentTrial'] != conf['nTrials']:
                resetMaxTrials(connection, conf['currentTrial']+1)
                return False
            return True

    def canCreditBeEdited(self, connection, trial):
        with self.lock:
            return countReceived(connection, trial) == 0

    def deleteTrialVotesForUser(self, connection, trial, user, judges):
        with self.lock:
            deleteTrialVotesForUser(connection, trial, user, judges)
            self.vote_deleted.emit(trial, user)

    def sendMessage(self, message):
        with self.lock:
            self._messageIndex += 1
            self._message = message

    def countIncomplete(self, connection, trial):
        with self.lock:
            return countIncomplete(connection, trial)


if __name__ == '__main__':
    c = apsw.Connection(":memory:")
    if checkDBVersion(c) != USER_DB_VERSION:
        print("Creating")
        createTableV2(c)
        today = datetime.date.today()
        setConfig(c, "test", today, 6, 100, 3, 0, 0, "uuid", 100)
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
