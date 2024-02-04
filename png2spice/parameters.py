from os.path import join

class CP2SParameters:
    def __init__(self) -> None:
        self.contrastThreshold          = 170
        self.imagePadding               = 70
        self.cannyThreshold             = 200
        self.pointDistance              = 50
        self.imageSliceSize             = 150   # The size of the subimages of POI analysis
        self.HLThreshold                = 6     # Hough Lines Transform threshold
        self.HLMinLineLength            = 48    # Hough Lines Transform minLineLength
        self.HLmaxLineGap               = 2     # Hough Lines Transform maxLineGap
        self.HoughIterations            = 10    # Amount of iterations
        self.HoughThresholdWiggle       = 15
        self.partSnapshotDir            = join(".temp", "output", "snapshots")
        self.DuplicateVariance          = 180
        self.ComponentTerminalVariance  = 80
        self.minGridStep                = 16

P2SParameters = CP2SParameters()