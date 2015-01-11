"""
Author: Bryan O'Malley
Date Created: 2015/01/11
Other Contributors:
Date Modified: 2015/01/11
Purpose: Generate PAC stats from SC2 Replay based
    on SkillCraft project research done by Mark Blair, Ph.D., et. al.
Skillcraft Source URL: http://skillcraft.ca/category/blog/
"""
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

from collections import defaultdict


class PACAnalyzer(object):
    name = 'PACAnalyzer'

    def handleInitGame(self, event, replay):
        for human in replay.humans:
            human.apm = defaultdict(int)
            human.aps = defaultdict(int)
            human.seconds_played = replay.length.seconds

    def handleControlGroupEvent(self, event, replay):
        event.player.aps[event.second] += 1
        event.player.apm[int(event.second/60)] += 1

    def handleSelectionEvent(self, event, replay):
        event.player.aps[event.second] += 1
        event.player.apm[int(event.second/60)] += 1

    def handleCommandEvent(self, event, replay):
        event.player.aps[event.second] += 1
        event.player.apm[int(event.second/60)] += 1

    def handlePlayerLeaveEvent(self, event, replay):
        event.player.seconds_played = event.second

    def handleEndGame(self, event, replay):
        for human in replay.humans:
            if len(human.apm.keys()) > 0:
                human.avg_apm = sum(human.aps.values())/float(human.seconds_played)*60
            else:
                human.avg_apm = 0
