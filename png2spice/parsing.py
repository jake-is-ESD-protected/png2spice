"""
This submodule of **png2spice** parses the virtual graph into LTSPICE
syntax and exports it as `.asc` file for LTSPICE to open. Sadly, the 
relationships of the LTSPICE part coordinatees and their terminals is
undocumented, which means that it had to be investigated manually. The
results are described and used below:

LT SPICE COMPONENT TO PLACEMENT ALIGNMENT
RESISTOR VER UPPER TERMINAL Y + 16
RESISTOR VER TERMINAL X + 16
RESISTOR VER LOWER TERMINAL Y - 96
RESISTOR HOR LEFT X -96
RESISTOR HOR LEFT Y +16
RESISTOR HOR RIGHT X -16
RESISTOR HOR RIGHT Y +16

CAPACITOR VER UPPER TERMINAL Y + 16
CAPACITOR VER TERMINAL X + 16
CAPACITOR VER LOWER TERMINAL Y + 64
CAPACITOR HOR LEFT X -64
CAPACITOR HOR LEFT Y +16
CAPACITOR HOR RIGHT Y +16

INDUCTOR VER UPPER TERMINAL X + 16
INDUCTOR VER UPPER TERMINAL Y + 16
INDUCTOR VER TERMINAL X + 16
INDUCTOR VER LOWER TERMINAL Y + 96
INDUCTOR HOR LEFT X - 96
INDUCTOR HOR LEFT Y + 16
INDUCTOR HOR RIGHT X -16
INDUCTOR HOR RIGHT Y + 16

DIODE VER UPPER TERMINAL X +16
DIODE VER TERMINAL X + 16
DIODE VER LOWER TERMINAL Y +64
DIODE HOR LEFT X - 64
DIODE HOR LEFT Y + 16
DIODE HOR RIGHT X
DIODE HOR RIGHT Y + 16
"""

from POI import POI, POITypes
from graphing import CGraph
from typing import List, Union

class CParser():
    def __init__(self, graph: Union[CGraph, List[POI]]) -> None:
        """
        BRIEF
        -----
        Create a parser objoect which consumes a `png2spice.graphing.CGraph`
        and converts it into a `.asc` file for LTSPICE.

        PARAMETERS
        ----------
        `graph`: `Union[CGraph, List[POI]]`
            Graph or list of POIs (loose graph).
        """
        if isinstance(graph, CGraph):
            self.graphContents = graph.looseGraph
        else:
            self.graphContents = graph
        self.header = "SHEET 1 1000 1000"
        self.part_aliases = dict({
            f"{POITypes.Resistor}": "res",
            f"{POITypes.Capacitor}": "cap",
            f"{POITypes.Inductor}": "ind",
            f"{POITypes.Diode}": "diode",
            f"{POITypes.Corner}": None,
            f"{POITypes.Junction}": None,
            f"{POITypes.Cross}": None,
            f"{POITypes.GND}": "0",            
        })


    def __Poi2Str(self, poi: POI) -> str:
        """
        BRIEF
        -----
        Convert a POI object into a single line in the LTSPICE
        syntax.

        PARAMETERS
        ----------
        `poi`: `png2spice.POI.POI`
            POI object to be converted.
        
        RETURNS
        -------
        `str`:
            POI as line in text format corresponding to LTSPICE
            syntax.
        """
        posx = poi.position[0]
        posy = poi.position[1]
        rot = str(poi.rotation)
        if poi.type.value <= POITypes.Diode.value:
            return f"SYMBOL {self.part_aliases[f'{poi.type}']} {posx} {posy} R{rot}"
        if poi.type.value == POITypes.GND.value:
            return f"FLAG {posx + 16} {posy} {self.part_aliases[f'{poi.type}']}"
        else:
            return ""

    def __GeneratePartOffset(self, POIType: POITypes, x: int, y: int, rot: int, terminal: str) -> str: # maybe make this a num
        """
        BRIEF
        -----
        Obtain the fitting part offset per part type as needed by LTSPICE.

        PARAMETERS
        ----------
        `POIType`: `png2spice.POI.POITypes`
            Desired POI type.
        `x`: `int`
            x-coordinate of part.
        `y`: `int`
            y-coordinate of part.
        `rot`: `int`
            rotation of part.
        `terminal`: `str`
            Primary terminal (A) or secondary terminal (B).

        RETURNS
        -------
        `str`:
            POI as line in text format corresponding to LTSPICE
            syntax.
        """
        if(POIType == POITypes.Resistor):
            if(rot == 0):
                if(terminal == "A"):
                    return f"{x + 16} {y + 16}"
                elif(terminal == "B"):
                    return f"{x + 16} {y + 96}"
            elif(rot == 90):
                if(terminal == "A"):
                    return f"{x - 96} {y + 16}"
                elif(terminal == "B"):
                    return f"{x - 16} {y + 16}"
        elif(POIType == POITypes.Capacitor):
            if(rot == 0):
                if(terminal == "A"):
                    return f"{x + 16} {y}"
                elif(terminal == "B"):
                    return f"{x + 16} {y + 64}"
            elif(rot == 90):
                if(terminal == "A"):
                    return f"{x - 64} {y + 16}"
                elif(terminal == "B"):
                    return f"{x } {y + 16}"
        elif(POIType == POITypes.Inductor):
            if(rot == 0):
                if(terminal == "A"):
                    return f"{x + 16} {y + 16}"
                elif(terminal == "B"):
                    return f"{x + 16} {y + 96}"
            elif(rot == 90):
                if(terminal == "A"):
                    return f"{x - 96} {y + 16}"
                elif(terminal == "B"):
                    return f"{x - 16} {y + 16}"
        elif(POIType == POITypes.Diode):
            if(rot == 0):
                if(terminal == "A"):
                    return f"{x + 16} {y + 0}"
                elif(terminal == "B"):
                    return f"{x + 16} {y +64}"
            elif(rot == 90):
                if(terminal == "A"):
                    return f"{x - 64} {y + 16}"
                elif(terminal == "B"):
                    return f"{x} {y + 16}"
        elif(POIType == POITypes.Corner or POIType == POITypes.Junction or POIType == POITypes.Cross):
            return f"{x+16} {y+16}"
        elif(POIType == POITypes.GND):
            return f"{x + 16} {y}"
        return "0 0"

    def __GenerateWire(self, startPOI: POI, terminal: str) -> str:
        """
        BRIEF
        -----
        Create LTSPICE syntax for wires.

        PARAMETERS
        ----------
        `startPOI`: `png2spice.POI.POI`
            First POI in graph.
        `terminal`: `str`
            Primary terminal (A) or secondary terminal (B).
            
        RETURNS
        -------
        `str`:
            Wire as line in text format corresponding to LTSPICE
            syntax.
        """
        startX = startPOI.position[0]
        startY = startPOI.position[1]
        rot = startPOI.rotation
        if(terminal == "A" and startPOI.terminalA is not None):
            return f"WIRE {self.__GeneratePartOffset(startPOI.type, startX, startY, startPOI.rotation, 'A')} {self.__GeneratePartOffset(startPOI.terminalA.type, startPOI.terminalA.position[0], startPOI.terminalA.position[1], startPOI.terminalA.rotation , 'A')}"
        elif(terminal == "B" and startPOI.terminalB is not None):
            return f"WIRE {self.__GeneratePartOffset(startPOI.type, startX, startY, startPOI.rotation, 'B')} {self.__GeneratePartOffset(startPOI.terminalB.type, startPOI.terminalB.position[0], startPOI.terminalB.position[1], startPOI.terminalB.rotation, 'B')}"
        else:
            return ""
        
    def Graph2Asc(self, save_path: str="./output.asc", graph: List[POI]=None):
        """
        BRIEF
        -----
        Iterate through all registered POIs in the graph and convert them
        into LTSPICE syntax.

        PARAMETERS
        ----------
        `save_path`: `str`
            Destination of `.asc` LTSPICE file to be saved.
            Default is `./output.asc`
        `graph`: `list[png2spice.POI.POI]`
            Graph to be converted. A graph is a list of POIs. If `graph` is 
            omitted, the graph passed at the creation of the `CParser` is
            used. Default is `None`.
        """
        if graph:
            if isinstance(graph, CGraph):
                self.graphContents = graph.looseGraph
            else:
                self.graphContents = graph
        with open(save_path, 'w') as f:
            f.write(self.header + "\n")
            for poi in self.graphContents:
                    f.write(self.__Poi2Str(poi) + "\n")
                    f.write(self.__GenerateWire(poi, "A") + "\n")
                    f.write(self.__GenerateWire(poi, "B") + "\n")