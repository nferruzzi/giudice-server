#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: MIT (see LICENSE)
"""
import sqlite3


class Gara(object):
    def __init__(self, description, nJudges, date, trials, nUsers):
        self.description = description
        self.nJudges = nJudges
        self.date = date
        self.trials = trials
        self.users = nUsers
