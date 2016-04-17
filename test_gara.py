#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: GPLv3 (see LICENSE)
"""
import unittest
from gara import *


class GaraBaseTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assertFEqual(self, a, b, precision=1E-10):
        v = abs(a-b)
        self.assertTrue(v < precision, "{} > {}".format(abs(a-b),precision))

    def registerUsers(self, n):
        for x in range(1, n+1):
            self.gara.registerJudgeWithUUID(self.connection, x, str(x)*3)

    def addVote(self, judge, user, vote, trial=0):
        user_uuid = str(judge)*3
        v = self.gara.addRemoteVote(self.connection,
                                    trial=trial,
                                    user=user,
                                    judge=judge,
                                    user_uuid=user_uuid,
                                    vote=vote)
        self.assertEqual(v[0], 200, v)


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


class BasicFunctionalityTrialsAdvance(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=1, nTrials=3, nUsers=10, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.registerUsers(1)

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote_fail_trial(self):
        v = self.gara.addRemoteVote(self.connection, trial=0, user=1, judge=1, user_uuid="111", vote=6.5)
        self.assertEqual(v[0], 200, v)
        v = self.gara.addRemoteVote(self.connection, trial=1, user=1, judge=1, user_uuid="111", vote=6.5)
        self.assertEqual(v[0], 403, v)
        v = self.gara.advanceToNextTrial(self.connection)
        self.assertEqual(v, (True, 1))
        v = self.gara.addRemoteVote(self.connection, trial=1, user=1, judge=1, user_uuid="111", vote=6.5)
        self.assertEqual(v[0], 200, v)

    def test_addvote_advance_too_much(self):
        v = self.gara.advanceToNextTrial(self.connection)
        self.assertEqual(v, (True, 1))
        v = self.gara.advanceToNextTrial(self.connection)
        self.assertEqual(v, (True, 2))
        v = self.gara.advanceToNextTrial(self.connection)
        self.assertEqual(v, (False, 3))
        v = self.gara.advanceToNextTrial(self.connection)
        self.assertEqual(v, (False, 3))


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
        self.assertFEqual(u['trials'][0]['votes'][1], 6.5)
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
        self.assertFEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertFEqual(u['trials'][0]['score'], 6.5)
        self.assertFEqual(u['trials'][0]['score_bonus'], 6.5)


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
        self.assertFEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertEqual(u['trials'][0]['score'], None)
        self.assertEqual(u['trials'][0]['score_bonus'], None)
        self.assertEqual(u['trials'][1]['votes'][1], None)
        self.assertEqual(u['trials'][1]['score'], None)
        self.assertEqual(u['trials'][1]['score_bonus'], None)

    def test_addvote_usercomplete(self):
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, vote=6.5)
        u = self.gara.getUser(self.connection, user=1)
        self.assertFEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertFEqual(u['trials'][0]['score'], 6.5)
        self.assertFEqual(u['trials'][0]['score_bonus'], 6.5)
        self.assertEqual(u.get('results'), None)


class BasicFunctionalityWithQueryCheckCompleteGara(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=6, nTrials=1, nUsers=10, average=Average_Aritmetica)
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
        self.assertFEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertEqual(u['trials'][0]['score'], None)
        self.assertEqual(u['trials'][0]['score_bonus'], None)

    def test_addvote_usercomplete(self):
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, vote=6.5)
        u = self.gara.getUser(self.connection, user=1)
        self.assertFEqual(u['trials'][0]['votes'][1], 6.5)
        self.assertFEqual(u['trials'][0]['score'], 6.5)
        self.assertFEqual(u['trials'][0]['score_bonus'], 6.5)
        self.assertFEqual(u['results']['average'], 6.5)
        self.assertFEqual(u['results']['average_bonus'], 6.5)
        self.assertFEqual(u['results']['sum'], 6.5)


class BasicFunctionalityWithQueryCheckAverageAritmetica(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=6, nTrials=2, nUsers=10, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.registerUsers(6)

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote_checkvalues(self):
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, vote=x)
        u = self.gara.getUser(self.connection, user=1)
        for x in range(0, 6):
            self.assertEqual(u['trials'][0]['votes'][x+1], x)

    def test_addvote_checkscore(self):
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, vote=0.25+x)
        u = self.gara.getUser(self.connection, user=1)
        self.assertFEqual(u['trials'][0]['score'], (0.25+1.25+2.25+3.25+4.25+5.25)/6.0)
        self.assertFEqual(u['trials'][0]['score_bonus'], (0.25+1.25+2.25+3.25+4.25+5.25)/6.0)

    def createAndTestVotesAritmetica(self, a, b):
        for x in range(0, 6):
            self.addVote(trial=0, judge=x+1, user=1, vote=a)
        self.gara.advanceToNextTrial(self.connection)
        for x in range(0, 6):
            self.addVote(trial=1, judge=x+1, user=1, vote=b)
        u = self.gara.getUser(self.connection, user=1)
        self.assertFEqual(u['trials'][0]['score'], a)
        self.assertFEqual(u['trials'][0]['score_bonus'], a)
        self.assertFEqual(u['trials'][0]['average'], a)
        self.assertFEqual(u['trials'][1]['score'], b)
        self.assertFEqual(u['trials'][1]['score_bonus'], b)
        self.assertFEqual(u['trials'][1]['average'], (a+b)/2.0)
        self.assertFEqual(u['results']['average'], (a+b)/2.0)
        self.assertFEqual(u['results']['average_bonus'], (a+b)/2.0)
        self.assertFEqual(u['results']['sum'], a+b)

    def test_addvote_checkscore_complete_1(self):
        self.createAndTestVotesAritmetica(5, 8)

    def test_addvote_checkscore_complete_2(self):
        self.createAndTestVotesAritmetica(1, 10)

    def test_addvote_checkscore_complete_3(self):
        self.createAndTestVotesAritmetica(0.5, 5.75)

    def test_addvote_checkscore_complete_4(self):
        self.createAndTestVotesAritmetica(3.25, 4.75)

    def test_addvote_checkscore_complete_5(self):
        self.createAndTestVotesAritmetica(3.2543, 4.7525)


class BasicFunctionalityWithQueryCheckAverageMediata(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=6, nTrials=3, nUsers=10, average=Average_Mediata)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.registerUsers(6)

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote_checkscore(self):
        votes = [1, 5, 6, 7, 8, 100]
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, vote=votes[x])
        u = self.gara.getUser(self.connection, user=1)
        votes.remove(min(votes))
        votes.remove(max(votes))
        self.assertFEqual(u['trials'][0]['score'], sum(votes)/len(votes))
        self.assertFEqual(u['trials'][0]['score_bonus'], sum(votes)/len(votes))

    def createAndTestVotesMediata(self, a, b, c):
        votes_a = [a, a*a, a*0.3, a*2, a*a*0.8, a*3]
        votes_b = [b, b*b, b*0.3, a*2, a*a*0.8, a*3]
        votes_c = [c, c*c, c*0.3, c*2, c*c*0.8, c*3]
        for x in range(0, 6):
            self.addVote(trial=0, judge=x+1, user=1, vote=votes_a[x])
        self.gara.advanceToNextTrial(self.connection)

        for x in range(0, 6):
            self.addVote(trial=1, judge=x+1, user=1, vote=votes_b[x])
        self.gara.advanceToNextTrial(self.connection)

        for x in range(0, 6):
            self.addVote(trial=2, judge=x+1, user=1, vote=votes_c[x])
        u = self.gara.getUser(self.connection, user=1)

        votes_a.remove(min(votes_a))
        votes_a.remove(max(votes_a))
        votes_b.remove(min(votes_b))
        votes_b.remove(max(votes_b))
        votes_c.remove(min(votes_c))
        votes_c.remove(max(votes_c))
        ma = sum(votes_a)/len(votes_a)
        mb = sum(votes_b)/len(votes_b)
        mc = sum(votes_c)/len(votes_c)

        self.assertFEqual(u['trials'][0]['score'], ma)
        self.assertFEqual(u['trials'][0]['score_bonus'], ma)
        self.assertFEqual(u['trials'][0]['average'], ma)
        self.assertFEqual(u['trials'][1]['score'], mb)
        self.assertFEqual(u['trials'][1]['score_bonus'], mb)
        self.assertFEqual(u['trials'][1]['average'], (ma+mb)/2.0)
        self.assertFEqual(u['trials'][2]['score'], mc)
        self.assertFEqual(u['trials'][2]['score_bonus'], mc)
        self.assertFEqual(u['trials'][2]['average'], (ma+mb+mc)/3.0)
        self.assertFEqual(u['results']['average'], (ma+mb+mc)/3.0)
        self.assertFEqual(u['results']['average_bonus'], (ma+mb+mc)/3.0)
        self.assertFEqual(u['results']['sum'], ma+mb+mc)

    def test_addvote_checkscore_complete_1(self):
        self.createAndTestVotesMediata(5, 8, 9)

    def test_addvote_checkscore_complete_2(self):
        self.createAndTestVotesMediata(1, 10, 2)

    def test_addvote_checkscore_complete_3(self):
        self.createAndTestVotesMediata(0.5, 5.75, 6.63)

    def test_addvote_checkscore_complete_4(self):
        self.createAndTestVotesMediata(3.25, 4.75, 5.12)

    def test_addvote_checkscore_complete_5(self):
        self.createAndTestVotesMediata(3.2543, 4.7525, 5.3432)


class BasicFunctionalityWithSimpleCredits(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=6, nTrials=3, nUsers=10, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.registerUsers(6)

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote_checkscore(self):
        bonus_1 = 1.0
        bonus_2 = 2.0
        bonus_3 = 3.0
        self.gara.updateUserInfo(self.connection, {1: {0: bonus_1, 1: bonus_2, 2: bonus_3}})
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, trial=0, vote=5)
        self.gara.advanceToNextTrial(self.connection)
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, trial=1, vote=6)
        self.gara.advanceToNextTrial(self.connection)
        for x in range(0, 6):
            self.addVote(judge=x+1, user=1, trial=2, vote=7)
        u = self.gara.getUser(self.connection, user=1)

        self.assertFEqual(u['trials'][0]['score_bonus'], 5+bonus_1)
        self.assertFEqual(u['trials'][1]['score_bonus'], 6+bonus_2)
        self.assertFEqual(u['trials'][2]['score_bonus'], 7+bonus_3)

        self.assertFEqual(u['trials'][0]['average'], 5)
        self.assertFEqual(u['trials'][1]['average'], (5+6)/2.0)
        self.assertFEqual(u['trials'][2]['average'], (5+6+7)/3.0)

        self.assertFEqual(u['trials'][0]['average_bonus'], 5+bonus_1)
        self.assertFEqual(u['trials'][1]['average_bonus'], (5+bonus_1+6+bonus_2)/2.0)
        self.assertFEqual(u['trials'][2]['average_bonus'], (5+bonus_1+6+bonus_2+7+bonus_3)/3.0)

        self.assertFEqual(u['results']['average'], (5+6+7)/3.0)
        self.assertFEqual(u['results']['average_bonus'], (5+bonus_1+6+bonus_2+7+bonus_3)/3.0)
        self.assertFEqual(u['results']['sum'], (5+bonus_1+6+bonus_2+7+bonus_3))


class BasicFunctionalityWithCreditsInsertion(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=6, nTrials=3, nUsers=10, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.registerUsers(6)

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote_checkscore(self):
        u = self.gara.getUserInfo(self.connection, 1)
        self.assertEqual(u['nickname'], '')
        for x in range(0, MAX_TRIALS):
            self.assertFEqual(u['credits'][x], 0.0)
        self.gara.updateUserInfo(self.connection, {1: {-1:'test', 0: 1, 4: 2, 8: 3}})
        u = self.gara.getUserInfo(self.connection, 1)
        self.assertEqual(u['nickname'], 'test')
        self.assertFEqual(u['credits'][0], 1.0)
        self.assertFEqual(u['credits'][4], 2.0)
        self.assertFEqual(u['credits'][8], 3.0)
        self.gara.updateUserInfo(self.connection, {1: {0: 0}})
        u = self.gara.getUserInfo(self.connection, 1)
        self.assertFEqual(u['credits'][0], 0.0)
        self.gara.updateUserInfo(self.connection, {2: {0: 0}})
        u = self.gara.getUserInfo(self.connection, 2)
        self.assertFEqual(u['credits'][0], 0.0)
        self.gara.updateUserInfo(self.connection, {2: {0: 1, -1: 'test'}})
        u = self.gara.getUserInfo(self.connection, 2)
        self.assertFEqual(u['credits'][0], 1.0)
        self.assertEqual(u['nickname'], 'test')


class BasicFunctionalityUserInfo(GaraBaseTest):

    def setUp(self):
        self.gara = Gara(nJudges=6, nTrials=3, nUsers=10, average=Average_Aritmetica)
        self.gara.createDB()
        self.connection = self.gara.connection
        self.gara.setState(self.connection, State_Running)
        self.registerUsers(6)

    def tearDown(self):
        self.connection = None
        self.gara = None

    def test_addvote_checkscore(self):
        u = self.gara.getUserInfo(self.connection, 1)
        self.assertEqual(u['nickname'], '')
        self.gara.updateUserInfo(self.connection, {1: {-1:'test'}})
        u = self.gara.getUserInfo(self.connection, 1)
        self.assertEqual(u['nickname'], 'test')


if __name__ == '__main__':
    unittest.main()
