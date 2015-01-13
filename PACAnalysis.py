#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

import os
import argparse

import sc2reader
from sc2reader import utils
from sc2reader.exceptions import ReadError
from sc2reader.engine.plugins.pacanalyzer import *

sc2reader.engine.register_plugin(PACAnalyzer())


def printReplay(filepath, analysis, arguments):
    """ Prints summary information about SC2 replay file """
    try:
        replay = sc2reader.load_replay(filepath, debug=True)

        if arguments.displayreplays:
            print("\n--------------------------------------\n{0}\n".format(filepath))
            print("   Map:      {0}".format(replay.map_name))
            print("   Date:     {0}".format(replay.start_time))
            print("   Version:  {0}".format(replay.release_string))
            print("   Length:   {0} minutes".format(replay.game_length))
            lineups = [team.lineup for team in replay.teams]
            print("   Teams:    {0}".format("v".join(lineups)))
            if len(replay.observers) > 0:
                print("   Observers:")
                for observer in replay.observers:
                    print("      {0}".format(observer.name))
        for team in replay.teams:
            if arguments.displayreplays:
                print("      Team {0}".format(team.number))
            for player in team.players[0:]:
                if arguments.displayreplays:
                    print("      \t{0} ({1})".format(player.name, player.pick_race[0]))
                    print("      \t\tPPM: {0:>6.2f}".format(player.PACStats.ppm))
                    print("      \t\tPAL: {0:>6.2f}".format(player.PACStats.pal))
                    print("      \t\tAPP: {0:>6.2f}".format(player.PACStats.app))
                    print("      \t\tGAP: {0:>6.2f}".format(player.PACStats.gap))
                if player.toon_id in analysis:
                    analysis[player.toon_id].ppm = (analysis[player.toon_id].count * analysis[player.toon_id].ppm +
                                                    player.PACStats.ppm) / (analysis[player.toon_id].count + 1)
                    analysis[player.toon_id].pal = (analysis[player.toon_id].count * analysis[player.toon_id].pal +
                                                    player.PACStats.pal) / (analysis[player.toon_id].count + 1)
                    analysis[player.toon_id].app = (analysis[player.toon_id].count * analysis[player.toon_id].app +
                                                    player.PACStats.app) / (analysis[player.toon_id].count + 1)
                    analysis[player.toon_id].gap = (analysis[player.toon_id].count * analysis[player.toon_id].gap +
                                                    player.PACStats.gap) / (analysis[player.toon_id].count + 1)
                    analysis[player.toon_id].count += 1
                else:
                    analysis[player.toon_id] = PACStats()
                    analysis[player.toon_id].name = player.name
                    analysis[player.toon_id].count = 1
                    analysis[player.toon_id].ppm = player.PACStats.ppm
                    analysis[player.toon_id].pal = player.PACStats.pal
                    analysis[player.toon_id].app = player.PACStats.app
                    analysis[player.toon_id].gap = player.PACStats.gap

        print
    except ReadError as e:
        raise
        return
        prev = e.game_events[-1]
        print("\nVersion {0} replay:\n\t{1}".format(e.replay.release_string, e.replay.filepath))
        print("\t{0}, Type={1:X}".format(e.msg, e.type))
        print("\tPrevious Event: {0}".format(prev.name))
        print("\t\t" + prev.bytes.encode('hex'))
        print("\tFollowing Bytes:")
        print("\t\t" + e.buffer.read_range(e.location, e.location + 30).encode('hex'))
        print("Error with '{0}': ".format(filepath))
        print(e)
    except Exception as e:
        print("Error with '{0}': ".format(filepath))
        print(e)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="""Prints PAC information from Starcraft II replay files or directories.""")
    parser.add_argument('--recursive', action="store_false", default=True,
                        help="Recursively read through directories of Starcraft II files [default on]")

    required = parser.add_argument_group('Required Arguments')
    required.add_argument('paths', metavar='filename', type=str, nargs='+',
                          help="Paths to one or more Starcraft II files or directories")

    display = parser.add_argument_group('Display Options')
    display.add_argument('--pausestats', action="store_false", default=True,
                        help="Pauses after each stat block [default on]")
    display.add_argument('--pausereplays', action="store_true", default=False,
                        help="Pauses after each replay summary [default off]")
    display.add_argument('--displayreplays', action="store_true", default=False,
                        help="Displays individual replay summaries [default off]")

    arguments = parser.parse_args()
    analysis = {}
    depth = -1 if arguments.recursive else 0
    replays = set(filepath for path in arguments.paths for filepath in utils.get_files(path, depth=depth) if os.path.splitext(filepath)[1].lower() == '.sc2replay')
    replayCount = len(replays)

    if replayCount == 1:
        arguments.displayreplays = True
        arguments.pausereplays = True

    for replay in replays:
        printReplay(replay, analysis, arguments)
        if arguments.pausereplays:
            print("PRESS ENTER TO CONTINUE")
            input()

    if replayCount > 1:
        print("\n--------------------------------------")
        print("Results - {0} Replays Analyzed".format(replayCount))
        print("{0} Players Analyzed".format(len(analysis)))
        for stats in sorted(analysis.items(), key=lambda t: t[1].count, reverse=True):
            print("\t{0:<15} (pid: {1})\t- {2} replays".format(stats[1].name, stats[0], stats[1].count))
            print("\t\tPPM: {0:>6.2f}".format(stats[1].ppm))
            print("\t\tPAL: {0:>6.2f}".format(stats[1].pal))
            print("\t\tAPP: {0:>6.2f}".format(stats[1].app))
            print("\t\tGAP: {0:>6.2f}".format(stats[1].gap))
            if arguments.pausestats:
                print("PRESS ENTER TO CONTINUE")
                input()

if __name__ == '__main__':
    main()
