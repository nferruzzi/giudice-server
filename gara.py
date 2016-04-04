#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: MIT (see LICENSE)
"""
from PyQt5.QtCore import QUuid, QStandardPaths
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
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


class Gara(object):
    def __init__(self,
                 description="Non configurata",
                 nJudges=0,
                 date=None,
                 trials=0,
                 nUsers=0):
        self.description = description
        self.nJudges = nJudges
        self.date = date
        self.trials = trials
        self.users = nUsers
        self.local_uuid = QUuid.createUuid().toString() + '.db'

    def createDB(self):
        dd = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        self.engine = create_engine('sqlite:///' + 'temp/' + self.local_uuid)
        Base.metadata.create_all(self.engine)
