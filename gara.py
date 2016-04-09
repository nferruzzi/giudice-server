#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: MIT (see LICENSE)
"""
from PyQt5.QtCore import QUuid, QStandardPaths, QDate, QObject, pyqtSignal, \
    QThread
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import datetime
import time
import threading
import pathlib

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user = Column(Integer)
    trial = Column(Integer)
    vote1 = Column(Float, nullable=True)
    vote2 = Column(Float, nullable=True)
    vote3 = Column(Float, nullable=True)
    vote4 = Column(Float, nullable=True)
    vote5 = Column(Float, nullable=True)
    vote6 = Column(Float, nullable=True)
    extra = Column(Integer, nullable=True)


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    date = Column(Date)
    nJudges = Column(Integer)
    nUsers = Column(Integer)
    nTrials = Column(Integer)
    currentTrial = Column(Integer)
    uuid = Column(String(250))


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
                 current=False):
        super(QObject, self).__init__()
        self._description = description
        self._nJudges = nJudges
        self._date = date if date is not None else QDate.currentDate()
        self._nTrials = nTrials
        self._nUsers = nUsers
        self._uuid = QUuid.createUuid().toString()
        self.current = current
        self.usersUUID = dict()
        self.usersTIME = dict()
        self._created = False
        where = QStandardPaths.TempLocation
        dd = QStandardPaths.writableLocation(where)
        pd = pathlib.Path(dd)
        pu = pathlib.Path(self._uuid + '.gara')
        self._path = pd / pu

    @staticmethod
    def setActiveInstance(gara):
        assert gara.scoped_session, "scoped session not available"
        with Gara.lock:
            Gara.activeInstance = gara
            print("Set active instance: ", gara)

    def createDB(self):
        assert not self._created, "already created"
        with self.lock:
            self._created = True
            print("Path: ", self._path)

            self.engine = create_engine('sqlite:///' + str(self._path),
                                        connect_args={
                                            'check_same_thread': False
                                        },
                                        echo=True)

            Base.metadata.create_all(self.engine)
            Base.metadata.bind = self.engine

            self.session_factory = sessionmaker(bind=self.engine)
            self.scoped_session = scoped_session(self.session_factory)

            session = self.scoped_session()
            conf = Config()
            conf.description = self._description
            conf.date = datetime.datetime(year=self._date.year(),
                                          month=self._date.month(),
                                          day=self._date.day())
            conf.nJudges = self._nJudges
            conf.nTrials = self._nTrials
            conf.nUsers = self._nUsers
            conf.uuid = self._uuid
            conf.currentTrial = 0

            session.add(conf)
            session.commit()

            self.scoped_session.remove()

    def getConfiguration(self, session):
        with self.lock:
            return session.query(Config).first()

    def state(self, session):
        with self.lock:
            configuration = self.getConfiguration(session)
            # Send message back to client
            state = {
                "current_trial": configuration.currentTrial,
                "max_trial": configuration.nTrials,
                "latest_user": 0,
                "max_user": configuration.nUsers,
                "uuid": configuration.uuid,
                "description": configuration.description,
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
            print(self.usersUUID)
            v = self.usersUUID.get(judge)
            if v is None:
                return False
            return v == uuid

    def addRemoteVote(self, session, judge, uuid, nTrial, nUser, vote):
        with self.lock:
            if session.query(User).filter(User.trial==nTrial).filter(User.user==nUser).count() == 0:
                print("Creating new row")
                user = User()
                user.user = nUser
                user.trial = nTrial
                session.add(user)
            else:
                user = session.query(User).filter(User.trial==nTrial).filter(User.user==nUser).first()

            if judge == 1:
                user.vote1 = vote
            elif judge == 2:
                user.vote2 = vote
            elif judge == 3:
                user.vote3 = vote
            elif judge == 4:
                user.vote4 = vote
            elif judge == 5:
                user.vote5 = vote
            elif judge == 6:
                user.vote6 = vote

            session.commit()
            print("Sent: ", threading.currentThread(), QThread.currentThread())
            self.vote_updated.emit(nTrial, nUser, judge, vote)

            return {}
