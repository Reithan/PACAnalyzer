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


class PAC:
    def __init__(self, frame, x, y):
        min, max = [x, y], [x, y]
        cameras = [[frame, x, y]]
        actions = []

    """
    tuplelist = [[5, 1, 2], [5, 2, 1], [5, 2, 2]]
    tuplesum = [sum(x) for x in zip(*tuplelist)]
    print(tuplesum[1:])
    """


class PACAnalyzer(object):
    name = 'PACAnalyzer'

    def handleInitGame(self, event, replay):
        """ Might not use PAC Grid calculation
        # Connect and load map for PAC grid calculations
        if not replay.map:
            replay.load_map()
        """
        # Settings for fixation
        replay.PACInfo.DispThreshold = 6
        replay.PACInfo.DurThreshold = 0.2
        for human in replay.humans:
            human.PACList = None

    def handleCameraEvent(self, event, replay):
        if not event.player.PACList:
            event.player.PACList = PAC(event.frame, event.x, event.y)
        else:
            newMin = [min(x) for x in zip(event.player.PACList[-1].min, [event.x, event.y])]
            newMax = [max(x) for x in zip(event.player.PACList[-1].max, [event.x, event.y])]
            diff = sum([abs(x[0] - x[1]) for x in zip(newMin, newMax)])
            if diff <= replay.PACInfo.DispThreshold:  # Within Dispersion window - Add to Fixation/PAC
                event.player.PACList[-1].cameras.append([event.frame, event.x, event.y])
                # recalculate PAC camera min & max
                event.player.PACList[-1].min = newMin
                event.player.PACList[-1].max = newMax
            else:
                # if the PAC is empty, or hasn't hit minimum time yet, shift selection window
                if len(event.player.PACList[-1].actions) == 0 or \
                        (event.player.PACList[-1].cameras[-1][0] - event.player.PACList[-1].cameras[0][0] <
                         replay.PACInfo.DurThreshold * 16): # 16 fps
                    event.player.PACList[-1].cameras.append([event.frame, event.x, event.y])
                    while diff > replay.PACInfo.DispThreshold:
                        del event.player.PACList[-1].cameras[0]
                        event.player.PACList[-1].min = [min(x) for x in zip(*event.player.PACList[-1].cameras)][1:]
                        event.player.PACList[-1].max = [max(x) for x in zip(*event.player.PACList[-1].cameras)][1:]
                        diff = sum(
                            [abs(x[0] - x[1]) for x in zip(event.player.PACList[-1].min, event.player.PACList[-1].max)])
                        for x in range(0,len(event.player.PACList[-1].actions)):
                            if event.player.PACList[-1].actions[x] < event.player.PACList[-1].cameras[0][0]:
                                del event.player.PACList[-1].actions[x]
                            else:
                                break
                else: # otherwise, simply add a new PAC
                    event.player.PACList.append(PAC(event.frame, event.x, event.y))


    def handleControlGroupEvent(self, event, replay):
        event.player.aps[event.second] += 1
        event.player.apm[int(event.second / 60)] += 1

    def handleSelectionEvent(self, event, replay):
        event.player.aps[event.second] += 1
        event.player.apm[int(event.second / 60)] += 1

    def handleCommandEvent(self, event, replay):
        event.player.aps[event.second] += 1
        event.player.apm[int(event.second / 60)] += 1

    def handlePlayerLeaveEvent(self, event, replay):
        event.player.seconds_played = event.second

    def handleEndGame(self, event, replay):
        for human in replay.humans:
            if len(human.apm.keys()) > 0:
                human.avg_apm = sum(human.aps.values()) / float(human.seconds_played) * 60
            else:
                human.avg_apm = 0
