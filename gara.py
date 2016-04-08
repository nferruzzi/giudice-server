#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: MIT (see LICENSE)
"""
from PyQt5.QtCore import QUuid, QStandardPaths, QDate
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import datetime
import threading

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

class Gara(object):

    DONOT_ALLOW_DUPLICATE_JUDGES = True

    def __init__(self,
                 description="Non configurata",
                 nJudges=0,
                 date=None,
                 nTrials=0,
                 nUsers=0,
                 current=False):
        self._description = description
        self._nJudges = nJudges
        self._date = date if date is not None else QDate.currentDate()
        self._nTrials = nTrials
        self._nUsers = nUsers
        self._uuid = QUuid.createUuid().toString() + '.db'
        self.current = current
        self.lock = threading.RLock()
        self.usersUUID = dict()

    def createDB(self):
        dd = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        if not self.current:
            self.engine = create_engine('sqlite:///:memory:')
        else:
            self.engine = create_engine('sqlite:///' + 'temp/' + self._uuid)

        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
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

        self.session.add(conf)
        self.session.commit()
        self.configuration = conf

    def state(self):
        # Send message back to client
        state = {
            "current_trial": self.configuration.currentTrial,
            "max_trial": self.configuration.nTrials,
            "latest_user": 0,
            "max_user": self.configuration.nUsers,
            "uuid": self.configuration.uuid,
            "description": self.configuration.description,
        }
        return state

    def registerJudgeWithUUID(self, judge, uuid):
        self.lock.acquire()

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

        self.lock.release()
        return present != uuid
