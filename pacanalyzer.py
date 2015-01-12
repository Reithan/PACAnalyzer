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
        if not event.player.PACList:
            event.player.PACList[-1].actions.append(event.frame)

    def handleSelectionEvent(self, event, replay):
        if not event.player.PACList:
            event.player.PACList[-1].actions.append(event.frame)

    def handleCommandEvent(self, event, replay):
        if not event.player.PACList:
            event.player.PACList[-1].actions.append(event.frame)

    """
    def handlePlayerLeaveEvent(self, event, replay):
        event.player.seconds_played = event.second
    """

    def handleEndGame(self, event, replay):
        for human in replay.humans:
            numPACs = len(human.PACList)
            # PAC per Minute
            human.PACStats.ppm = numPACs / (replay.frames / (16 * 60))  # 16fps, 60s/min
            # PAC action latency
            human.PACStats.pal = (sum(PAC.actions[0] - PAC.cameras[0][0]) for PAC in human.PACList) / numPACs
            # Actions per PAC
            human.PACStats.app = (sum(len(PAC.actions)) for PAC in human.PACList) / numPACs
            # Gap between PAC
            human.PACStats.gap = (sum(human.PACList[x + 1][0] - human.PACList[x][0]) for x in range(0,numPACs - 1)) / (numPACs - 1)