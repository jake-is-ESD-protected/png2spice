from os.path import join

class CP2SParameters:
    def __init__(self) -> None:
        self.contrastThreshold          = 170
        self.imagePadding               = 1200
        self.cannyThreshold             = 200
        self.pointDistance              = 850
        self.imageSliceSize             = 2955   # The size of the subimages of POI analysis
        self.HLThreshold                = 75     # Hough Lines Transform threshold
        self.HLMinLineLength            = 940    # Hough Lines Transform minLineLength
        self.HLmaxLineGap               = 2     # Hough Lines Transform maxLineGap
        self.HoughIterations            = 10    # Amount of iterations
        self.HoughThresholdWiggle       = 15
        self.partSnapshotDir            = join(".temp", "output", "snapshots")
        self.DuplicateVariance          = 2581
        self.ComponentTerminalAVariance  = 1800
        self.ComponentTerminalBVariance  = 2400
        self.minGridStep                = 16
        self.scalingFactor              = 0

    def setScalingFactor(self, scalingFactor) -> float:
        self.scalingFactor = scalingFactor

P2SParameters = CP2SParameters()