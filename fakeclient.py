#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2018 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: GPLv3 (see LICENSE)
"""
import requests
from multiprocessing import Pool, Process
import random
import time

KEEP_ALIVE = "http://localhost:8000/keepAlive"
VOTE = "http://localhost:8000/vote"

KEEP_ALIVE = "http://192.168.43.147:8000/keepAlive"
VOTE = "http://192.168.43.147:8000/vote"

class Client:
    def __init__(self, judge):
        self.judge = str(judge)
        self.keepAlive()

    def keepAlive(self):
        ka = requests.get(KEEP_ALIVE + "/" + self.judge, headers={'X-User-Auth': self.judge})
        json = ka.json()
        self.currentTrial = json['current_trial']
        print(ka.json())

    def vote(self, trial, user, vote):
        time.sleep(1.0)
        self.keepAlive()
        return requests.post(VOTE, headers={'X-User-Auth': self.judge}, json={"judge": self.judge, "trial": trial, "user": user, "vote": vote})    

def doIt(client):
    for user in range(1, 101):
        try:
            client.vote(client.currentTrial, user, random.randint(0, 10))
        except:
            pass

if __name__ == '__main__':
    clients = [Client(x) for x in range(1, 7)]
    with Pool(processes=6) as pool:
        pool.map(doIt, clients)
