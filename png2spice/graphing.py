"""
This submodule of **png2spice** deals with the virtual representation
of the analyzed schematic. Here, virtual graph assembly is performed and 
values are optimized based on an analytical approach with thresholds
visible in `png2spice.parameters.py`. 
"""

import numpy as np
from POI import POI, POITypes, isValidPOI, pred2Type
import math
from parameters import P2SParameters

class CGraph:
    def __init__(self, lines: np.ndarray, preds: dict, ocrs: dict) -> None:
        """
        BRIEF
        -----
        Create a graph-object which holds the detected parts and their connections.

        PARAMETERS
        ----------
        `lines`:
            `np.ndarray`. Line coordinates obtained from `png2spice.lines.getHoughLines`.
        `preds`:
            `dict`. Dictionary of predictions obtained from `png2spice.inference.CSPICEnet.predict`.
        `ocrs`:
            `dict`. Dictionary of OCR detections obtained from `png2spice.inference.CSPICEnet.predict`.

        NOTES
        -----
        The graph does not hold the schematic as dimensional data. Translation into 
        x/y coordinates is done in `png2spice.parsing.CParser`.
        """
        self.lines = lines
        self.looseGraph = list()
        for i, line in enumerate(lines):
            classifications = list(preds[f"{i}A"].values())
            ocr = None
            if ocrs:
                if f"{i}A" in ocrs.keys():
                    ocr = ocrs[f"{i}A"]
            if isValidPOI(classifications):
                self.looseGraph.append(POI(f"{i}A",
                                           line[0:2],
                                           pred2Type(classifications),
                                           ocr))
            
            classifications = list(preds[f"{i}B"].values())
            ocr = None
            if ocrs:
                if f"{i}B" in ocrs.keys():
                    ocr = ocrs[f"{i}B"]
            if isValidPOI(classifications):
                self.looseGraph.append(POI(f"{i}B",
                                           line[2:4],
                                           pred2Type(classifications),
                                           ocr))


    def rmDuplicates(self):
        """
        BRIEF
        -----
        Remove most likely duplicates in the graph via a treshold setting based on
        proximity.

        NOTES
        -----
        Modifies the graph's contents in place. Contains **P2S parameters** `DuplicateVariance` and `scalingFactor`.
        """
        v = int(P2SParameters.DuplicateVariance * P2SParameters.scalingFactor)
        for poi1 in self.looseGraph:
            for i, poi2 in enumerate(self.looseGraph):
                dist = math.dist(tuple(poi1.position),tuple(poi2.position))
                if(poi1 != poi2 and dist < v and poi1.type == poi2.type):
                    del self.looseGraph[i]
    

    def link(self):
        """
        BRIEF
        -----
        Link components stored in graph.

        NOTES
        -----
        Modifies the graph's contents in place. Contains **P2S parameters** `ComponentTerminalAVariance` and `ComponentTerminalBVariance`.
        """
        ComponentTerminalAVariance = int(P2SParameters.ComponentTerminalAVariance * P2SParameters.scalingFactor)
        ComponentTerminalBVariance = int(P2SParameters.ComponentTerminalBVariance * P2SParameters.scalingFactor)
        for lG in self.looseGraph:
            for line in self.lines:
                if(math.dist(lG.position, line[0:2]) < ComponentTerminalBVariance):
                    if(lG.terminalBLine is None):
                        lG.terminalBLine = line[2:4]
                    elif(lG.terminalALine is None):
                        lG.terminalALine = line[2:4]

        for lG1 in self.looseGraph:
            for lG2 in self.looseGraph:
                if(lG1.terminalALine is not None and lG1.terminalA is None and (math.dist(lG2.position, lG1.terminalALine) < ComponentTerminalAVariance)):
                    if(lG1.terminalA is None):
                        lG1.terminalA = lG2
                elif(lG1.terminalBLine is not None and lG1.terminalB is None and (math.dist(lG2.position, lG1.terminalBLine) < ComponentTerminalBVariance)):
                    if(lG1.terminalB is None):
                        lG1.terminalB = lG2
    
    def angle_of_line(self, p1: tuple, p2: tuple):
        """
        BRIEF
        -----
        Get the angle between two points represented by a touple of x/y coordinates.

        PARAMETERS
        ----------
        `p1`:
            `tuple`. Starting point.
        `p2`:
            `tuple`. Ending point.
        
        RETURNS
        ------
        `float`. Angle of line relative to base x-axis.
        """
        return math.degrees(math.atan2(-(p2[1]-p1[1]), p2[0]-p1[0]))

    def analyzeRotations(self):
        """
        BRIEF
        -----
        Analyze the rotations of components based on the coordinates of their
        terminals.

        NOTES
        -----
        Modifies the graph's contents in place. 
        """
        skipped = [POITypes.Corner, POITypes.Junction, POITypes.Diode]
        for lG in self.looseGraph:
            if(lG.terminalALine is not None):
                if(abs(self.angle_of_line(lG.terminalALine, lG.position)) > 45 and abs(self.angle_of_line(lG.terminalALine, lG.position)) < 165):
                    lG.rotation = 0
                else:
                    lG.rotation = 90 # COMPENTS LAY
                
            if(lG.terminalBLine is not None):
                if(abs(self.angle_of_line(lG.terminalBLine, lG.position)) > 45 and abs(self.angle_of_line(lG.terminalBLine, lG.position)) < 165):
                    lG.rotation = 0
                else:
                    lG.rotation = 90 # COMPENTS LAY
    
    def snapToGrid(self):
        """
        BRIEF
        -----
        Align all stored coordinates to a grid with a minimum step size.

        NOTES
        -----
        Modifies the graph's contents in place. Contains **P2S parameters** `minGridStep`.
        """
        d = P2SParameters.minGridStep
        for poi in self.looseGraph:
            x, y = tuple(poi.position)
            poi.position = tuple(((x + d//2) // d * d, (y + d//2) // d * d))


    def alignToGrid(self):
        """
        BRIEF
        -----
        Align all stored coordinates to a grid derived from the detected
        component positions as to maintain a good looking form usual for
        a schematic.

        NOTES
        -----
        Modifies the graph's contents in place. Contains **P2S parameters** `minGridStep`.
        """
        d = P2SParameters.minGridStep
        margin = (d*2, d*2)
        for poi1 in self.looseGraph:
            for poi2 in self.looseGraph:
                if(poi1.rotation == poi2.rotation):
                    if(poi1.rotation == 0):
                        # snap to same x-axis
                        if abs(poi1.position[0] - poi2.position[0]) < margin[0]:
                            poi2.position = (poi1.position[0], poi2.position[1])
                    elif poi1.rotation == 90:
                        # snap to same y-axis
                        if abs(poi1.position[1] - poi2.position[1]) < margin[1]:
                            poi2.position = (poi2.position[0], poi1.position[1])
                    else:
                        print("[GRID ALIGN WARN]: Rotation is higher than 90°")
                if(poi1.type == POITypes.Corner or poi1.type == POITypes.Junction or poi1.type == POITypes.GND):
                    if abs(poi1.position[0] - poi2.position[0]) < margin[0]:
                        poi2.position = (poi1.position[0], poi2.position[1])
                    if abs(poi1.position[1] - poi2.position[1]) < margin[1]:
                        poi2.position = (poi2.position[0], poi1.position[1])