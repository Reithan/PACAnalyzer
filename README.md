# PACAnalyzer
Perception-Action Cycle analysis plugin for SC2Reader

This plugin is built based on the work of Mark Blair, Ph.D, et.al on the SkillCraft project. You can find their blog at:
http://skillcraft.ca/category/blog/

This plugin adds a list of PACs to each human player in a replay.

The list consists of PAC objects with the following attributes
* **min, max**: Min & max camera coordinates for this fixation
* **cameras**: list of camera actions during this PAC, formatted as [frame#, x, y] for each camera action in the list
* **actions**: list of frame numbers actions were taken on during this PAC

Additionally, a PACInfo object is added to the replay with the attributes DispThreshold and DurThreshold. DispThreshold is the max combined x & y shift before a new fixation is started while DurThreshold is the minimum duration for a camera location to be considered a fixation.

Finally, a PACStats object is added to each human player with the following statistics calculated:
* **ppm**: average(mean) PAC per minute
* **pal**: PAC action latency. e.g: how long it takes you to take your first action after each fixation shift. (mean average)
* **app**: Actions per PAC. The average(mean) number of actions you take each PAC.
* **gap**: How long it takes you, after finishing your actions in one PAC to establish a new fixation. (mean average)
