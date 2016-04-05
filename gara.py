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


class Gara(object):
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
        self.local_uuid = QUuid.createUuid().toString() + '.db'
        self.current = current

    def createDB(self):
        dd = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        if not self.current:
            self.engine = create_engine('sqlite:///:memory:')
        else:
            self.engine = create_engine('sqlite:///' + 'temp/' + self.local_uuid)

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
        conf.currentTrial = 0
        self.session.add(conf)
        self.session.commit()
        self.configuration = conf
