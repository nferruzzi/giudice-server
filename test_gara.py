#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: MIT (see LICENSE)
"""
import unittest
from gara import *


class GaraBaseTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def registerUsers(self, n):
        for x in range(1, n+1):
            self.gara.registerJudgeWithUUID(self.connection, x, str(x)*3)

    def addVote(self, judge, user, vote):
        user_uuid = str(judge)*3
        v = self.gara.addRemoteVote(self.connection,
                                    trial=0,
                                    user=user,
                                    judge=judge,
                                    user_uuid=user_uuid,
                                    vote=vote)
        self.assertEqual(v[0], 200)


class BasicFunctionality(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=1, nTrials=1, nUsers=1, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.gara.registerJudgeWithUUID(self.connection, 1, "abc")

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote(self):
        v = self.gara.addRemoteVote(self.connection, trial=0, user=1, judge=1, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 200)

    def test_addvote_duplucate(self):
        v = self.gara.addRemoteVote(self.connection, trial=0, user=1, judge=1, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 200)
        v = self.gara.addRemoteVote(self.connection, trial=0, user=1, judge=1, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 403)

    def test_addvote_pettorina0_specialcase(self):
        v = self.gara.addRemoteVote(self.connection, trial=0, user=1, judge=1, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 200)
        v = self.gara.addRemoteVote(self.connection, trial=0, user=0, judge=1, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 200)

    def test_addvote_outofrange(self):
        # trial
        v = self.gara.addRemoteVote(self.connection, trial=1, user=1, judge=1, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 403)
        # user too high
        v = self.gara.addRemoteVote(self.connection, trial=0, user=2, judge=1, user_uuid="abc", vote=6.5)
        # user too low (but no 0)
        v = self.gara.addRemoteVote(self.connection, trial=0, user=-1, judge=1, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 403)
        # judge not accepted min
        v = self.gara.addRemoteVote(self.connection, trial=0, user=1, judge=0, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 403)
        # judge not accepted max
        v = self.gara.addRemoteVote(self.connection, trial=0, user=1, judge=2, user_uuid="abc", vote=6.5)
        self.assertEqual(v[0], 403)
        # judge fake
        v = self.gara.addRemoteVote(self.connection, trial=0, user=1, judge=1, user_uuid="zzz", vote=6.5)
        self.assertEqual(v[0], 403)


class BasicFunctionalityJudges(GaraBaseTest):

    def tearDown(self):
        self.connection = None
        self.gara = None

    def setUp(self):
        self.gara = Gara(nJudges=2, nTrials=1, nUsers=1, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)

    def test_register(self):
        # valid register
        code, _ = self.gara.registerJudgeWithUUID(self.connection, 1, "abc")
        self.assertEqual(code, 200)
        # steal attempt
        code, _ = self.gara.registerJudgeWithUUID(self.connection, 1, "def")
        self.assertEqual(code, 403)
        # judge unregister
        code, _ = self.gara.registerJudgeWithUUID(self.connection, 2, "abc")
        self.assertEqual(code, 200)
        # judge replace
        code, _ = self.gara.registerJudgeWithUUID(self.connection, 1, "def")
        self.assertEqual(code, 200)

    def test_register_overflow(self):
        # valid register
        code, _ = self.gara.registerJudgeWithUUID(self.connection, 3, "XXX")
        self.assertEqual(code, 404)
        code, _ = self.gara.registerJudgeWithUUID(self.connection, 0, "XXX")
        self.assertEqual(code, 404)


class BasicFunctionalityWithQueryCheck(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=6, nTrials=2, nUsers=10, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.registerUsers(6)

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote_single(self):
        self.addVote(judge=1, user=1, vote=6.5)
        u = self.gara.getUser(self.connection, user=1)
        self.assertEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertEqual(u['trials'][0]['score'], None)
        self.assertEqual(u['trials'][0]['score_bonus'], None)

    def test_addvote_usercomplete(self):
        self.addVote(judge=1, user=1, vote=6.5)
        self.addVote(judge=2, user=1, vote=6.5)
        self.addVote(judge=3, user=1, vote=6.5)
        self.addVote(judge=4, user=1, vote=6.5)
        self.addVote(judge=5, user=1, vote=6.5)
        self.addVote(judge=6, user=1, vote=6.5)
        u = self.gara.getUser(self.connection, user=1)
        self.assertEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertEqual(u['trials'][0]['score'], 6.5)
        self.assertEqual(u['trials'][0]['score_bonus'], 6.5)

class BasicFunctionalityWithQueryCheck(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=6, nTrials=2, nUsers=10, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.registerUsers(6)

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote_single(self):
        self.addVote(judge=1, user=1, vote=6.5)
        u = self.gara.getUser(self.connection, user=1)
        self.assertEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertEqual(u['trials'][0]['score'], None)
        self.assertEqual(u['trials'][0]['score_bonus'], None)
        self.assertEqual(u['trials'][1]['votes'][1], None)
        self.assertEqual(u['trials'][1]['score'], None)
        self.assertEqual(u['trials'][1]['score_bonus'], None)

    def test_addvote_usercomplete(self):
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, vote=6.5)
        u = self.gara.getUser(self.connection, user=1)
        self.assertEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertEqual(u['trials'][0]['score'], 6.5)
        self.assertEqual(u['trials'][0]['score_bonus'], 6.5)
        self.assertEqual(u.get('results'), None)

if __name__ == '__main__':
    unittest.main()
