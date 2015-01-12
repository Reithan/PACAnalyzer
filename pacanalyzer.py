"""
Author: Bryan O'Malley (bo122081@hotmail.com)
Date Created: 2015/01/11
Other Contributors:
Date Modified: 2015/01/11
Purpose: Plugin for SC2Reader
    (https://github.com/GraylinKim/sc2reader)
    to Generate PAC stats from SC2 Replay based
    on SkillCraft project research done by Mark Blair, Ph.D. and the Simon Fraser University Cognitive Science Lab
Simon Fraser University Cognitive Science Lab URL: http://cslab-sfu.ca/
Skillcraft Source URL: http://skillcraft.ca/
"""
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

from collections import defaultdict


class PAC:
    def __init__(self, frame, x, y):
        self.min, self.max = [x, y], [x, y]
        self.cameras = [[frame, x, y]]
        self.actions = []

class PACInfo:
    def __init__(self, disp, dur):
        self.DispThreshold = disp
        self.DurThreshold = dur

class PACStats:
    ppm, pal, app, gap = None, None, None, None

class PACAnalyzer(object):
    name = 'PACAnalyzer'

    def handleInitGame(self, event, replay):
        """ Might not use PAC Grid calculation
        # Connect and load map for PAC grid calculations
        if not replay.map:
            replay.load_map()
        """
        # Settings for fixation
        replay.PACInfo = PACInfo(6, 0.2)
        for human in replay.humans:
            human.PACList = None

    def handleCameraEvent(self, event, replay):
        if not event.player.PACList:
            event.player.PACList = [PAC(event.frame, event.x, event.y)]
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
                         replay.PACInfo.DurThreshold * 16):  # 16 fps
                    event.player.PACList[-1].cameras.append([event.frame, event.x, event.y])
                    while diff > replay.PACInfo.DispThreshold:
                        del event.player.PACList[-1].cameras[0]
                        event.player.PACList[-1].min = [min(x) for x in zip(*event.player.PACList[-1].cameras)][1:]
                        event.player.PACList[-1].max = [max(x) for x in zip(*event.player.PACList[-1].cameras)][1:]
                        diff = sum(
                            [abs(x[0] - x[1]) for x in zip(event.player.PACList[-1].min, event.player.PACList[-1].max)])
                        for x in range(0,len(event.player.PACList[-1].actions) + 1):
                            if x == len(event.player.PACList[-1].actions) or\
                                            event.player.PACList[-1].actions[x] >= event.player.PACList[-1].cameras[0][0]:
                                del event.player.PACList[-1].actions[0:x]
                                break
                else: # otherwise, simply add a new PAC
                    event.player.PACList.append(PAC(event.frame, event.x, event.y))


    def handleControlGroupEvent(self, event, replay):
        if event.player.PACList:
            event.player.PACList[-1].actions.append(event.frame)

    def handleSelectionEvent(self, event, replay):
        if event.player.PACList:
            event.player.PACList[-1].actions.append(event.frame)

    def handleCommandEvent(self, event, replay):
        if event.player.PACList:
            event.player.PACList[-1].actions.append(event.frame)

    """
    def handlePlayerLeaveEvent(self, event, replay):
        event.player.seconds_played = event.second
    """

    def handleEndGame(self, event, replay):
        for human in replay.humans:
            if human.PACList:
                numPACs = len(human.PACList)
                human.PACStats = PACStats()
                # PAC per Minute
                human.PACStats.ppm = numPACs / (replay.frames / (16 * 60))  # 16fps, 60s/min
                # PAC action latency
                human.PACStats.pal = sum(iPAC.actions[0] - iPAC.cameras[0][0] for iPAC in human.PACList) /\
                    (numPACs * 16)
                # Actions per PAC
                human.PACStats.app = sum(len(iPAC.actions) for iPAC in human.PACList) / numPACs
                # Gap between PAC
                human.PACStats.gap = sum(human.PACList[x + 1].cameras[0][0] - human.PACList[x].actions[-1]
                                         for x in range(0, numPACs - 1)) / ((numPACs - 1) * 16)