"""
This submodule of **png2spice** defines the points of interest (POIs)
by which the virtual graph of components is organized. 
"""

import numpy as np
from enum import Enum

class POITypes(Enum):
   Resistor = 0
   Capacitor = 1
   Inductor = 2
   Diode = 3
   Corner = 4
   Junction = 5
   Cross = 6
   GND = 7

   @classmethod
   def get_index(cls, type):
      return list(cls).index(type)

class POI:
   def __init__(self):
      self.type = None
      self.position = None
      self.rotation = 90
      self.terminalA = None
      self.terminalB = None
      self.terminalC = None
      self.terminalD = None
      self.terminalALine = None
      self.terminalBLine = None
      self.terminalCLine = None
      self.terminalDLine = None
      self.value = None
      self.text = None
      self.marker = False
      self.name = None

   def __init__(self, val, pos, typ, name):
      self.type = typ
      self.position = pos
      self.rotation = 90
      self.terminalA = None
      self.terminalB = None
      self.terminalC = None
      self.terminalD = None
      self.terminalALine = None
      self.terminalBLine = None
      self.terminalCLine = None
      self.terminalDLine = None
      self.value = val
      self.text = None
      self.marker = False
      self.name = name
      self.confidence = 0

   def printType(self):
      print("My type is " + str(self.type))

   def getPosition(self):
      print("My position is " + str(self.position))
   
   def printInfo(self):
      if(self != None):
         print("Hi I am: " + str(self.value) + " and I am a " + str(self.type) + " @ " + str(self.position) + " " + str(self.name) + " R:" + str(self.rotation))


def isValidPOI(classList):
   return np.amax(classList) > 0.95

def pred2Type(POI):
   s = np.argmax(POI)
   return POITypes(s)