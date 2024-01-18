from .POI import POI, POITypes
from typing import List

# TODO: Anything WIRE-related

class CParser():
    def __init__(self, graph: List[POI]) -> None:
        self.graph = graph
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
        posx = str(poi.position[0])
        posy = str(poi.position[1])
        rot = str(poi.rotation)
        if poi.type.value <= POITypes.Diode.value:
            return f"SYMBOL {self.part_aliases[f'{poi.type}']} {posx} {posy} R{rot}"
        if poi.type.value == POITypes.GND.value:
            return f"FLAG {posx} {posy} {self.part_aliases[f'{poi.type}']}"
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
            self.graph = graph
        with open(save_path, 'w') as f:
            f.write(self.header + "\n")
            for poi in self.graph:
                f.write(self.__Poi2Str(poi) + "\n")
            