# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 02:48:14 2017

@author: Will
@author: Chunyuan Li
@author: Ethan Zheng
"""

import sys
import os
import re
import types

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from math import log10, floor

sys.path.append(re.sub('PlantRootsRelease', 'python', os.getcwd()))
from TraitsTabWidget import Ui_TraitsTabWidget
from EditingTabWidget import Ui_EditingTabWidget
from VisualizationTabWidget import Ui_VisualizationTabWidget
from RootsTool import Point3d, RootAttributes, Skeleton, mgraph

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import test_glviewer as tgl

############# Mode Enum #############

NO_MODE = 0
CONNECTION_MODE = 1
BREAK_MODE = 2
EDGE_SPLITTING_MODE = 3
COMPONENT_REMOVAL_MODE = 4

SELECT_TOP_NODE_MODE = 5
SELECT_BOTTOM_NODE_MODE = 6

SELECT_PRIMARY_NODES_MODE = 7
SELECT_PRIMARY_BRANCHES_MODE = 8
SELECT_SEGMENT_POINT_MODE = 9
VIEW_NODE_INFO_MODE = 10

DEFAULT_EDGE_HEATMAP_TYPE = 9
DEFAULT_NODE_HEATMAP_TYPE = 0
DEFAULT_EDGE_COLORIZATION_TYPE = 0
DEFAULT_NODE_COLORIZATION_TYPE = 0
HEATMAP_NONE_TYPE_COLOR = [1.0, 0.0, 0.0, 1.0]

def getColorList(size, colormap):
    colorList = []
    minval = 0
    maxval = 1
    for i in range(0, size):
        colorList.append(i)
        maxval = i

    norm = plt.Normalize(minval, maxval)
    listFormat = colormap(norm(colorList))

    return listFormat.tolist()


def round_to_2(x):
    return round(x, -int(floor(log10(abs(x)))) + 1)


class VisualizationTabWidget(Ui_VisualizationTabWidget, QObject):

    viewSkeleton = pyqtSignal(bool)
    viewGraph = pyqtSignal(bool)
    viewBoth = pyqtSignal(bool)

    backgroundColorChanged = pyqtSignal(float, float, float)
    loadMeshSig = pyqtSignal()

    def getHeatmap(self, idx: int):
        if idx == 0:
            return [HEATMAP_NONE_TYPE_COLOR]
        else:
            return getColorList(1000, cm.get_cmap(self.heatmapOptions[idx]))

    @pyqtSlot(int)
    def edgeColorizationChanged(self, optionId: int):
        if optionId == 0:  # thickness
            self.graph.colorizeEdgesByThickness()
            pass
        elif optionId == 1:  # width
            self.graph.colorizeEdgesByWidth()
            pass
        elif optionId == 2:  # thickness / width
            self.graph.colorizeEdgesByRatio()
            pass
        elif optionId == 3:  # component
            self.graph.colorizeEdgesByComponent()
            pass

    @pyqtSlot(int)
    def nodeColorizationChanged(self, optionId: int):
        if optionId == 0:  # thickness
            self.graph.colorizeNodesByThickness()
            pass
        elif optionId == 1:  # width
            self.graph.colorizeNodesByWidth()
            pass
        elif optionId == 2:  # degree
            self.graph.colorizeNodesByDegree()
            pass
        elif optionId == 3:  # component
            self.graph.colorizeNodesByComponent()
            pass
        elif optionId == 4:  # flat node color
            self.graph.colorizeNodesByConstantColor()

    @pyqtSlot(int)
    def nodeHeatmapChanged(self, optionId: int):
        heatmap = self.getHeatmap(optionId)
        self.graph.assignNodeHeatmap(heatmap)

    @pyqtSlot(int)
    def edgeHeatmapChanged(self, optionId: int):
        heatmap = self.getHeatmap(optionId)
        self.graph.assignEdgeHeatmap(heatmap)

    @pyqtSlot(int)
    def junctionScaleChanged(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        self.graph.setJunctionScale(scale)

    @pyqtSlot(int)
    def endpointScaleChanged(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        self.graph.setEndpointScale(scale)

    @pyqtSlot(int)
    def edgeScaleChanged(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        scale = max(scale, 1.0)
        self.graph.setEdgeScale(scale)

    @pyqtSlot()
    def edgeColorFloorChanged(self):
        sliderVal = self.edgeColorFloor.value()
        floor = 1.0 * sliderVal / 100.0
        if not self.edgeColorFloor.isSliderDown():
            self.graph.setEdgeColorFloor(floor)

    @pyqtSlot()
    def edgeColorCeilingChanged(self):
        sliderVal = self.edgeColorCeiling.value()
        ceiling = 1.0 * sliderVal / 100.0
        self.graph.setEdgeColorCeiling(ceiling)

    @pyqtSlot()
    def nodeColorFloorChanged(self):
        sliderVal = self.nodeColorFloor.value()
        floor = 1.0 * sliderVal / 100.0
        self.graph.setNodeColorFloor(floor)

    @pyqtSlot()
    def nodeColorCeilingChanged(self):
        sliderVal = self.nodeColorCeiling.value()
        ceiling = 1.0 * sliderVal / 100.0
        self.graph.setNodeColorCeiling(ceiling)

    @pyqtSlot(bool)
    def showHideJunctionsPressed(self):
        self.graph.showHideJunctions()

    @pyqtSlot(bool)
    def showHideEndpointsPressed(self):
        self.graph.showHideEndpoints()

    @pyqtSlot(bool)
    def showEdgesPressed(self, showEdges: bool):
        self.graph.showEdges(showEdges)

    @pyqtSlot(bool)
    def magnifyNonBridgesPressed(self, magnifyNonBridges: bool):
        self.graph.magnifyNonBridges(magnifyNonBridges)

    @pyqtSlot(bool)
    def showOnlyNonBridgesPressed(self, showOnly: bool):
        self.graph.showOnlyNonBridges(showOnly)

    @pyqtSlot(bool)
    def backgroundColorClicked(self, active):
        pickedColor = QColorDialog.getColor(
            self.currentBackground, self.widget)
        self.backgroundColorChanged.emit(
            pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentBackground = pickedColor

    @pyqtSlot(bool)
    def constantNodeColorClicked(self, active):
        pickedColor = QColorDialog.getColor(
            self.currentNodeColor, self.widget)
        self.graph.setConstantNodeColor(
            pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentNodeColor = pickedColor

    @pyqtSlot(bool)
    def edgeSelectionColorClicked(self, active):
        pickedColor = QColorDialog.getColor(
            self.currentEdgeSelectionColor, self.widget)
        self.graph.setEdgeSelectionColor(
            pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentEdgeSelectionColor = pickedColor

    @pyqtSlot(bool)
    def loadMeshClicked(self, active: bool):
        self.loadMeshSig.emit()

    @pyqtSlot(bool)
    def meshColorClicked(self, active: bool):
        pickedColor = QColorDialog.getColor(
            self.currentMeshColor, self.widget)
        self.graph.setMeshColor(
            pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentMeshColor = pickedColor

    @pyqtSlot(bool)
    def displayMeshClicked(self, doShow: bool):
        self.graph.showMesh(doShow)

    @pyqtSlot()
    def meshAlphaChanged(self):
        alphaInt = self.meshAlpha.value()
        alpha = 1.0 * alphaInt / 100.0
        self.graph.setMeshAlpha(alpha)

    def __init__(self, widget, graphObject: mgraph, viewSkeletonButton, viewGraphButton, viewBothButton):
        Ui_VisualizationTabWidget.__init__(self)
        QObject.__init__(self)
        self.setupUi(widget)
        self.widget = widget
        self.graph = graphObject
        self.currentBackground = QColor(255, 255, 255)
        self.currentNodeColor = QColor(0, 0, 0)
        self.currentEdgeSelectionColor = QColor(255, 255, 255)
        self.currentMeshColor = QColor(0, 0, 255)

        self.graph.setConstantNodeColor(
            self.currentNodeColor.redF(),
            self.currentNodeColor.greenF(),
            self.currentNodeColor.blueF())
        self.graph.setEdgeSelectionColor(
            self.currentEdgeSelectionColor.redF(),
            self.currentEdgeSelectionColor.greenF(),
            self.currentEdgeSelectionColor.blueF())

        self.graph.setMeshColor(
            self.currentMeshColor.redF(),
            self.currentMeshColor.greenF(),
            self.currentMeshColor.blueF())

        self.edgeColorizationOptions = {}
        self.edgeColorizationOptions[0] = "Thickness"
        self.edgeColorizationOptions[1] = "Width"
        self.edgeColorizationOptions[2] = "Thick/Width"
        self.edgeColorizationOptions[3] = "Component"

        self.nodeColorizationOptions = {}
        self.nodeColorizationOptions[0] = "Thickness"
        self.nodeColorizationOptions[1] = "Width"
        self.nodeColorizationOptions[2] = "Degree"
        self.nodeColorizationOptions[3] = "Component"
        self.nodeColorizationOptions[4] = "Flat Color"
        self.heatmapOptions = {}
        self.heatmapOptions[0] = "None"
        self.heatmapOptions[1] = "viridis"
        self.heatmapOptions[2] = "plasma"
        self.heatmapOptions[3] = "inferno"
        self.heatmapOptions[4] = "magma"
        self.heatmapOptions[5] = "hot"
        self.heatmapOptions[6] = "cool"
        self.heatmapOptions[7] = "gist_heat"
        self.heatmapOptions[8] = "BuGn"
        self.heatmapOptions[9] = "jet"

        for key in self.edgeColorizationOptions:
            self.edgeColorization.addItem(self.edgeColorizationOptions[key])

        for key in self.nodeColorizationOptions:
            self.nodeColorization.addItem(self.nodeColorizationOptions[key])

        for key in self.heatmapOptions:
            self.edgeHeatmapType.addItem(self.heatmapOptions[key])
            self.nodeHeatmapType.addItem(self.heatmapOptions[key])

        self.edgeColorization.currentIndexChanged.connect(
            self.edgeColorizationChanged)
        self.nodeColorization.currentIndexChanged.connect(
            self.nodeColorizationChanged)
        self.edgeHeatmapType.currentIndexChanged.connect(
            self.edgeHeatmapChanged)
        self.nodeHeatmapType.currentIndexChanged.connect(
            self.nodeHeatmapChanged)

        self.edgeColorization.setCurrentIndex(DEFAULT_EDGE_COLORIZATION_TYPE)
        self.nodeColorization.setCurrentIndex(DEFAULT_NODE_COLORIZATION_TYPE)
        self.edgeHeatmapType.setCurrentIndex(DEFAULT_EDGE_HEATMAP_TYPE)
        self.nodeHeatmapType.setCurrentIndex(DEFAULT_NODE_HEATMAP_TYPE)

        self.showHideEndpoints.clicked.connect(self.showHideEndpointsPressed)
        self.showHideJunctions.clicked.connect(self.showHideJunctionsPressed)
        self.showEdges.toggled.connect(self.showEdgesPressed)
        self.magnifyNonBridges.toggled.connect(self.magnifyNonBridgesPressed)
        self.displayOnlyNonBridges.toggled.connect(
            self.showOnlyNonBridgesPressed)

        self.backgroundColor.clicked.connect(self.backgroundColorClicked)
        self.constantNodeColor.clicked.connect(self.constantNodeColorClicked)
        self.edgeSelectionColor.clicked.connect(self.edgeSelectionColorClicked)

        self.showEdges.setChecked(True)
        self.magnifyNonBridges.setChecked(False)

        self.loadMeshButton.clicked.connect(self.loadMeshClicked)
        self.meshColorButton.clicked.connect(self.meshColorClicked)
        self.displayMesh.toggled.connect(self.displayMeshClicked)

        self.displayMesh.setChecked(False)

        # setting slider callbacks and values
        self.edgeScale.valueChanged.connect(self.edgeScaleChanged)
        self.junctionScale.valueChanged.connect(self.junctionScaleChanged)
        self.endpointScale.valueChanged.connect(self.endpointScaleChanged)
        self.edgeColorFloor.sliderReleased.connect(self.edgeColorFloorChanged)
        self.edgeColorCeiling.sliderReleased.connect(
            self.edgeColorCeilingChanged)
        self.nodeColorFloor.sliderReleased.connect(self.nodeColorFloorChanged)
        self.nodeColorCeiling.sliderReleased.connect(
            self.nodeColorCeilingChanged)
        self.meshAlpha.sliderReleased.connect(self.meshAlphaChanged)

        self.edgeColorFloor.setSliderDown(True)
        self.edgeColorCeiling.setSliderDown(True)
        self.nodeColorFloor.setSliderDown(True)
        self.nodeColorCeiling.setSliderDown(True)
        self.meshAlpha.setSliderDown(True)
        self.edgeScale.setValue(20)
        self.junctionScale.setValue(5)
        self.endpointScale.setValue(5)
        self.edgeColorFloor.setValue(0)
        self.edgeColorCeiling.setValue(100)
        self.nodeColorFloor.setValue(0)
        self.nodeColorCeiling.setValue(100)
        self.meshAlpha.setValue(30)
        self.edgeColorFloor.setSliderDown(False)
        self.edgeColorCeiling.setSliderDown(False)
        self.nodeColorFloor.setSliderDown(False)
        self.nodeColorCeiling.setSliderDown(False)
        self.meshAlpha.setSliderDown(False)

        self.viewSkeleton.emit(True)


class EditingTabWidget(Ui_EditingTabWidget, QObject):

    modeChangeSig = pyqtSignal(int)

    @pyqtSlot(bool)
    def showOnlySelected(self, doShow: bool):
        self.showSelected = doShow
        if self.mode == CONNECTION_MODE:
            if self.graph != None:
                self.graph.setDisplayOnlySelectedComponents(self.showSelected)

    @pyqtSlot(int)
    def componentOneChanged(self, component: int):
        self.component1 = component
        if self.mode == CONNECTION_MODE:
            if self.graph != None:
                self.graph.setComponent1(component)

    @pyqtSlot(int)
    def componentTwoChanged(self, component: int):
        self.component2 = component
        if self.mode == CONNECTION_MODE:
            if self.graph != None:
                self.graph.setComponent2(component)

    @pyqtSlot(bool)
    def showBoundingBoxes(self, doShow: bool):
        self.showBoxes = doShow
        if self.mode == CONNECTION_MODE:
            if self.graph != None:
                self.graph.setShowBoundingBoxes(self.showBoxes)

    @pyqtSlot(bool)
    def connectionModePressed(self, pressed: bool):
        self.changeMode(CONNECTION_MODE)

    @pyqtSlot(bool)
    def acceptConnectionPressed(self, pressed: bool):
        if self.mode == CONNECTION_MODE:
            self.graph.joinOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def breakModePressed(self, pressed: bool):
        self.changeMode(BREAK_MODE)

    @pyqtSlot(bool)
    def removeComponentPressed(self, pressed: bool):
        self.changeMode(COMPONENT_REMOVAL_MODE)

    @pyqtSlot(bool)
    def splitEdgeModePressed(self, pressed: bool):
        self.changeMode(EDGE_SPLITTING_MODE)

    @pyqtSlot(bool)
    def acceptRemovalPressed(self, pressed: bool):
        if self.mode == BREAK_MODE:
            if self.graph != None:
                self.graph.breakOperation()
                self.updateWidget()
        if self.mode == EDGE_SPLITTING_MODE:
            if self.graph != None:
                self.graph.splitOperation()
                self.updateWidget()
        # add code to c++
        if self.mode == COMPONENT_REMOVAL_MODE:
            if self.graph != None:
                print('enter c++ for remove component')
                self.graph.removeComponentOperation()
                self.updateWidget()

    def __init__(self, graphObject: mgraph, widget=None):
        Ui_EditingTabWidget.__init__(self)
        QObject.__init__(self)
        self.setupUi(widget)
        self.widget = widget
        self.graph = graphObject
        self.showSelected = False
        self.showBoxes = False
        self.mode = NO_MODE
        self.component1 = 0
        self.component2 = 0

        self.showOnlySelectedButton.toggled.connect(self.showOnlySelected)
        self.showBoundingBoxesButton.toggled.connect(self.showBoundingBoxes)
        self.ComponentOne.currentIndexChanged.connect(self.componentOneChanged)
        self.ComponentTwo.currentIndexChanged.connect(self.componentTwoChanged)
        self.ConnectionModeButton.clicked.connect(self.connectionModePressed)
        self.AcceptConnectionButton.clicked.connect(
            self.acceptConnectionPressed)
        self.BreakModeButton.clicked.connect(self.breakModePressed)
        self.SplitModeButton.clicked.connect(self.splitEdgeModePressed)
        self.AcceptRemovalButton.clicked.connect(self.acceptRemovalPressed)
        self.RemoveComponentButton.clicked.connect(self.removeComponentPressed)

    def changeMode(self, mode: int):
        if self.mode != mode or mode > 5:
            self.mode = mode
            print("changing mode")
            if self.graph != None:
                self.graph.unselectAll()
                self.updateWidget()
                if mode != CONNECTION_MODE:
                    self.graph.setDisplayOnlySelectedComponents(False)
                    self.graph.setShowBoundingBoxes(False)
                if mode == CONNECTION_MODE:
                    self.graph.setDisplayOnlySelectedComponents(
                        self.showSelected)
                    self.graph.setShowBoundingBoxes(self.showBoxes)
                # self.graph.setDisplayStem(False)
                # self.graph.setDisplayPrimaryNodes(False)
            self.modeChangeSig.emit(self.mode)

    def exitCurrentMode(self):
        pass

    def setGraph(self, graph: mgraph):
        print("setting graph")
        self.graph = graph
        self.updateWidget()
        if self.mode == CONNECTION_MODE and self.graph != None:
            self.graph.setDisplayOnlySelectedComponents(self.showSelected)
            self.graph.setShowBoundingBoxes(self.showBoxes)

    def updateWidget(self):
        if self.graph != None:
            edgesString = str(self.graph.getNumEdgesToBreak())
            self.edgesToBreak.setText(edgesString)

            self.ComponentOne.currentIndexChanged.disconnect(
                self.componentOneChanged)
            self.ComponentTwo.currentIndexChanged.disconnect(
                self.componentTwoChanged)

            self.ComponentOne.clear()
            self.ComponentTwo.clear()

            componentSizes = self.graph.getComponentSizes()
            numComponents = self.graph.getNumComponents()
            for i in range(0, numComponents):
                descriptor = str(i) + ' - ' + \
                    str(round_to_2(componentSizes[i]))
                self.ComponentOne.addItem(descriptor)
                self.ComponentTwo.addItem(descriptor)

            self.component1 = max(self.component1, 0)
            self.component2 = max(self.component2, 0)
            self.component1 = min(self.component1, numComponents - 1)
            self.component2 = min(self.component2, numComponents - 1)

            self.ComponentOne.setCurrentIndex(self.component1)
            self.ComponentTwo.setCurrentIndex(self.component2)
            self.graph.setComponent1(self.component1)
            self.graph.setComponent2(self.component2)

            self.ComponentOne.currentIndexChanged.connect(
                self.componentOneChanged)
            self.ComponentTwo.currentIndexChanged.connect(
                self.componentTwoChanged)
        else:
            self.edgesToBreak.setText("")
            self.ComponentOne.clear()
            self.ComponentTwo.clear()


class TraitsTabWidget(Ui_TraitsTabWidget, QObject):
    modeChangeSig = pyqtSignal(int)
    loadTraitsSig = pyqtSignal()
    saveTraitsSig = pyqtSignal()

    @pyqtSlot(bool)
    def loadTraitsPressed(self, pressed: bool):
        self.changeMode(SELECT_PRIMARY_BRANCHES_MODE)
        self.loadTraitsSig.emit()
        self.updateWidget()

    @pyqtSlot(bool)
    def saveTraitsPressed(self, pressed: bool):
        self.saveTraitsSig.emit()

    @pyqtSlot(bool)
    def selectTopNodePressed(self, pressed: bool):
        if self.graph != None:
            self.graph.setMode(SELECT_TOP_NODE_MODE)

    @pyqtSlot(bool)
    def selectBottomNodePressed(self, pressed: bool):
        if self.graph != None:
            self.graph.setMode(SELECT_BOTTOM_NODE_MODE)

    @pyqtSlot(bool)
    def ViewNodeInfoPressed(self, pressed: bool):
        self.changeMode(VIEW_NODE_INFO_MODE)

    @pyqtSlot(bool)
    def showHideStemPressed(self, pressed: bool):
        if self.graph != None:
            self.graph.showHideStem()

    @pyqtSlot(bool)
    def FindStemPressed(self, pressed: bool):
        try:
            self.stemLowThreshold = float(self.LowThresholdLineEdit.text())
        except ValueError:
            self.stemLowThreshold = int(self.LowThresholdLineEdit.text())
        if self.graph != None:
            self.graph.FindStemOperation(self.stemLowThreshold)
            self.updateWidget()

    @pyqtSlot(bool)
    def FindPrimaryNodePressed(self, Pressed: bool):
        try:
            self.nodeNeighbourRange = float(self.NodeIntervalLineEdit.text())
        except ValueError:
            self.nodeNeighbourRange = int(self.NodeIntervalLineEdit.text())

        try:
            self.Kernel_bandWidth = float(self.BandWidthLineEdit.text())
        except ValueError:
            self.Kernel_bandWidth = int(self.BandWidthLineEdit.text())

        if self.graph != None:
            self.graph.FindPrimaryNodeOperation(
                self.nodeNeighbourRange, self.Kernel_bandWidth)
            self.updateWidget()

    @pyqtSlot(bool)
    def showHideWhorlPressed(self, pressed: bool):
        if self.graph != None:
            self.graph.showHideWhorl()

    @pyqtSlot(bool)
    def deleteWhorlPressed(self, pressed: bool):
        if self.graph != None:
            self.graph.deleteWhorl()
            
    @pyqtSlot(bool)
    def showClusterInputChecked(self, doShow: bool):
        if self.graph != None:
            self.graph.setDisplayClusterInput(doShow)
            
    @pyqtSlot(bool)
    def tracePrimaryBranchesChecked(self, doTrace: bool):
        if self.graph != None:
            self.graph.setDisplayTracingPrimaryBranches(doTrace)
            
    @pyqtSlot(bool)
    def showBranchTracingChecked(self, doShow: bool):
        if self.graph != None:
            self.graph.setDisplayTracingTree(doShow)

    @pyqtSlot(bool)
    def selectStemPrimaryNodePressed(self, pressed: bool):
        self.changeMode(SELECT_PRIMARY_NODES_MODE)

    @pyqtSlot(bool)
    def confirmPrimaryNodesPressed(self, pressed: bool):
        if self.mode == SELECT_PRIMARY_NODES_MODE and self.graph:
            self.graph.selectStemPrimaryNodeOperation()
            self.updateWidget()

    @pyqtSlot(int)
    def currentPrimaryNodeChanged(self, node: int):
        self.currentPrimaryNode = node
        if self.graph != None:
            self.graph.setCurrentPrimaryNode(self.currentPrimaryNode)

    @pyqtSlot(bool)
    def selectPrimaryBranchesPressed(self, pressed: bool):
        self.changeMode(SELECT_PRIMARY_BRANCHES_MODE)

    @pyqtSlot(bool)
    def confirmPrimaryBranchesPressed(self, pressed: bool):
        if self.mode == SELECT_PRIMARY_BRANCHES_MODE and self.graph:
            self.graph.selectPrimaryBranchesOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def removePrimaryBranchesPressed(self, pressed: bool):
        if self.mode == SELECT_PRIMARY_BRANCHES_MODE and self.graph:
            self.graph.RemovePrimaryBranchesOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def PrimaryNodeSelectionColorPressed(self, active):
        pickedColor = QColorDialog.getColor(
            self.currentPrimaryNodeSelectionColor, self.widget)
        self.graph.setCurrentPrimaryNodeSelectionColor(
            pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentPrimaryNodeSelectionColor = pickedColor

    @pyqtSlot(bool)
    def showConfirmedPrimaryBranchesChecked(self, doShow: bool):
        self.showConfirmedPrimaryBranches = doShow
        if self.mode == SELECT_PRIMARY_BRANCHES_MODE:
            if self.graph != None:
                self.graph.setDisplayConfirmedPrimaryBranches(
                    self.showConfirmedPrimaryBranches)

    @pyqtSlot(bool)
    def showOnlyBranchesOfCurrentPrimaryNodeChecked(self, doShow: bool):
        self.showOnlyBranchesOfCurrentPrimaryNode = doShow
        if self.mode == SELECT_PRIMARY_BRANCHES_MODE and self.graph != None:
            self.graph.setDisplayOnlyBranchesOfCurrentPrimaryNode(
                self.showOnlyBranchesOfCurrentPrimaryNode)

    @pyqtSlot(bool)
    def showTraitsOnlyChecked(self, doShow: bool):
        self.showTraitsOnly = doShow
        if self.graph != None:
            self.graph.setDisplayTraitsOnly(self.showTraitsOnly)

    @pyqtSlot(bool)
    def SelectSegmentPointPressed(self, pressed: bool):
        self.changeMode(SELECT_SEGMENT_POINT_MODE)

    @pyqtSlot(bool)
    def ConfirmSegmentPointPressed(self):
        if self.mode == SELECT_SEGMENT_POINT_MODE and self.graph:
            self.graph.selectSegmentPointOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def showSelectedSegmentChecked(self, doShow: bool):
        self.showSelectedSegment = doShow
        if self.graph != None:
            self.graph.setDisplaySelectedSegment(self.showSelectedSegment)

    @pyqtSlot()
    def horizontalSliderRadiusChanged(self):
        sliderVal = self.horizontalSliderRadius.value()
        if not self.horizontalSliderRadius.isSliderDown():
            self.graph.setSegmentHorizontalSliderRadius(sliderVal)

    def __init__(self, graphObject: mgraph, widget=None):
        Ui_TraitsTabWidget.__init__(self)
        QObject.__init__(self)
        self.setupUi(widget)
        self.widget = widget
        self.graph = graphObject
        self.mode = NO_MODE
        self.currentPrimaryNode = 0
        self.showConfirmedPrimaryBranches = False
        self.showOnlyBranchesOfCurrentPrimaryNode = False
        self.showSelectedSegment = False
        self.showTraitsOnly = False

        self.stemLowThreshold = 0
        self.nodeNeighbourRange = 0
        self.Kernel_bandWidth = 0

        self.currentPrimaryNodeSelectionColor = QColor(255, 255, 255)
        self.graph.setCurrentPrimaryNodeSelectionColor(
            self.currentPrimaryNodeSelectionColor.redF(),
            self.currentPrimaryNodeSelectionColor.greenF(),
            self.currentPrimaryNodeSelectionColor.blueF())

        self.loadTraitsButton.clicked.connect(self.loadTraitsPressed)
        self.saveTraitsButton.clicked.connect(self.saveTraitsPressed)

        # manual find stem
        self.SelectTopNodeButton.clicked.connect(self.selectTopNodePressed)
        self.SelectBottomNodeButton.clicked.connect(self.selectBottomNodePressed)

        # automatic find stem
        self.ViewNodeInfoButton.clicked.connect(self.ViewNodeInfoPressed)
        self.showHideStemButton.clicked.connect(self.showHideStemPressed)
        self.FindStemButton.clicked.connect(self.FindStemPressed)

        # manual find primary nodes
        self.SelectPriamryNodeButton.clicked.connect(
            self.selectStemPrimaryNodePressed)
        self.ConfirmPrimaryNodesButton.clicked.connect(
            self.confirmPrimaryNodesPressed)
        # automatic find primary nodes
        self.showHideWhorlButton.clicked.connect(self.showHideWhorlPressed)
        self.deleteWhorlButton.clicked.connect(self.deleteWhorlPressed)
        self.showClusterInputCheck.toggled.connect(
            self.showClusterInputChecked)
        self.tracePrimaryBranchesCheck.toggled.connect(
            self.tracePrimaryBranchesChecked)
        self.showBranchTracingCheck.toggled.connect(
            self.showBranchTracingChecked)
        self.FindPrimaryNodesButton.clicked.connect(
            self.FindPrimaryNodePressed)

        self.PrimaryNodeSelectionColorButton.clicked.connect(
            self.PrimaryNodeSelectionColorPressed)

        self.CurrentPrimaryNodeCombo.currentIndexChanged.connect(
            self.currentPrimaryNodeChanged)
        self.SelectPrimaryBranchesButton.clicked.connect(
            self.selectPrimaryBranchesPressed)
        self.ConfirmPrimaryBranchesButton.clicked.connect(
            self.confirmPrimaryBranchesPressed)
        self.RemovePrimaryBranchesButton.clicked.connect(
            self.removePrimaryBranchesPressed)
        self.showConfirmedPrimaryBranchesCheck.toggled.connect(
            self.showConfirmedPrimaryBranchesChecked)
        self.showOnlyBranchesOfCurrentPrimaryNodeCheck.toggled.connect(
            self.showOnlyBranchesOfCurrentPrimaryNodeChecked)
        self.showTraitsOnlyCheck.toggled.connect(self.showTraitsOnlyChecked)

        self.SelectSegmentPointButton.clicked.connect(
            self.SelectSegmentPointPressed)
        self.ConfirmSegmentPointButton.clicked.connect(
            self.ConfirmSegmentPointPressed)
        self.showSelectedSegmentCheck.toggled.connect(
            self.showSelectedSegmentChecked)

        self.horizontalSliderRadius.sliderReleased.connect(
            self.horizontalSliderRadiusChanged)
        self.horizontalSliderRadius.setSliderDown(True)
        self.horizontalSliderRadius.setValue(10)
        self.horizontalSliderRadius.setSliderDown(False)

    def changeMode(self, mode: int):
        if self.mode != mode or mode < 6:
            self.mode = mode
            print("changing mode")
            if self.graph != None:
                self.graph.unselectAll()
                self.updateWidget()
                if mode != CONNECTION_MODE:
                    self.graph.setDisplayOnlySelectedComponents(False)
                    self.graph.setShowBoundingBoxes(False)
                if mode == CONNECTION_MODE:
                    self.graph.setDisplayOnlySelectedComponents(
                        self.showSelected)
                    self.graph.setShowBoundingBoxes(self.showBoxes)
                # if mode != CONNECTION_MODE and mode != EDGE_SPLITTING_MODE \
                #         and mode != BREAK_MODE \
                #         and mode != COMPONENT_REMOVAL_MODE:
                    # self.graph.setDisplayStem(self.showStem)
                    # self.graph.setDisplayPrimaryNodes(self.showPrimaryNodes)
                # else:
                    # self.graph.setDisplayStem(False)
                    # self.graph.setDisplayPrimaryNodes(False)
            self.modeChangeSig.emit(self.mode)

    def exitCurrentMode(self):
        pass

    def setGraph(self, graph: mgraph):
        print("setting graph")
        self.graph = graph
        self.updateWidget()
        # if self.graph != None:
        #     if self.mode != CONNECTION_MODE and self.mode != EDGE_SPLITTING_MODE \
        #             and self.mode != BREAK_MODE \
        #             and self.mode != COMPONENT_REMOVAL_MODE:
                # self.graph.setDisplayStem(self.showStem)
                # self.graph.setDisplayPrimaryNodes(self.showPrimaryNodes)
            # else:
                # self.graph.setDisplayStem(False)
                # self.graph.setDisplayPrimaryNodes(False)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def updateWidget(self):
        print("updateWidget")
        if self.graph != None:
            # update current primary node combo
            self.CurrentPrimaryNodeCombo.currentIndexChanged.disconnect(
                self.currentPrimaryNodeChanged)
            self.CurrentPrimaryNodeCombo.clear()
            numPrimaryNodes = self.graph.getNumPrimaryNodes()
            if numPrimaryNodes > 0:
                for i in range(0, numPrimaryNodes):
                    descriptor = str(i)
                    self.CurrentPrimaryNodeCombo.addItem(descriptor)
            else:
                self.CurrentPrimaryNodeCombo.clear()

            self.currentPrimaryNode = max(self.currentPrimaryNode, 0)
            self.currentPrimaryNode = min(
                self.currentPrimaryNode, numPrimaryNodes - 1)

            self.CurrentPrimaryNodeCombo.setCurrentIndex(
                self.currentPrimaryNode)
            self.graph.setCurrentPrimaryNode(self.currentPrimaryNode)
            self.CurrentPrimaryNodeCombo.currentIndexChanged.connect(
                self.currentPrimaryNodeChanged)
        else:
            self.CurrentPrimaryNodeCombo.clear()


class RootsTabbedProgram(QMainWindow):

    @pyqtSlot()
    def notifyConfirmed(self):
        print('Notify confirmed')

    @pyqtSlot()
    def terminateConfirmed(self):
        print('Terminate confirmed')

    @pyqtSlot()
    def mainPrint(self, toPrint: object):
        print(toPrint)

    @pyqtSlot()
    def acceptPressed(self):
        print('accept pressed')

    @pyqtSlot(int)
    def tabChanged(self, tabPos):
        if tabPos == 0:
            pass
        if tabPos == 1:
            self.enterConnectionMode()
            pass
        if tabPos == 2:
            self.enterBreakMode()
            pass
        if tabPos == 3:
            self.enterSplitMode()
            pass
        if tabPos == 4:
            self.enterRemoveComponentMode()
            pass
        if tabPos == 6:
            self.enterSelectStemMode()
            pass
        if tabPos == 7:
            self.enterSelectStemPrimaryNodeMode()
            pass
        if tabPos == 8:
            self.enterSelectPrimaryBranchesMode()
            pass

    def __init__(self, parent = None):
        super(RootsTabbedProgram, self).__init__(parent)
        
        self.currentMode = -2
        self.glwidget = tgl.GLWidget(self)
        self.dockedWidget = None
        self.__setUI()

    def __setUI(self, title="RootsEditor"):
        self.mainMenu = self.menuBar()

        self.mainMenu.setNativeMenuBar(False)
        self.fileMenu = self.mainMenu.addMenu('File')

        loadButton = QAction('Load rootfile', self)
        loadButton.setShortcut('Ctrl+L')
        loadButton.setShortcutContext(Qt.ApplicationShortcut)
        loadButton.setStatusTip('Load rootfile or skeleton')
        loadButton.triggered.connect(self.loadFile)
        self.fileMenu.addAction(loadButton)

        loadMeshButton = QAction('Load mesh file', self)
        loadMeshButton.setShortcut('Ctrl+M')
        loadMeshButton.setShortcutContext(Qt.ApplicationShortcut)
        loadMeshButton.setStatusTip('Load root mesh')
        loadMeshButton.triggered.connect(self.loadMesh)
        self.fileMenu.addAction(loadMeshButton)

        saveButton = QAction('Save rootfile', self)
        saveButton.setShortcut('Ctrl+S')
        saveButton.setShortcutContext(Qt.ApplicationShortcut)
        saveButton.setStatusTip('Save rootfile')
        saveButton.triggered.connect(self.saveFile)
        self.fileMenu.addAction(saveButton)

        saveFairedButton = QAction('Save Faired Skeleton as New File', self)
        saveFairedButton.setShortcut('Ctrl+Shift+S')
        saveFairedButton.setShortcutContext(Qt.ApplicationShortcut)
        saveFairedButton.setStatusTip('Perform Fairing on Current Skeleton and Save It as New File')
        saveFairedButton.triggered.connect(self.saveFairedSkeletonClicked)
        self.fileMenu.addAction(saveFairedButton)

        loadTraitsButton = QAction('Load Traits', self)
        loadTraitsButton.triggered.connect(self.loadTraitsFile)
        self.fileMenu.addAction(loadTraitsButton)

        saveTraitsButton = QAction('Save Traits', self)
        saveTraitsButton.triggered.connect(self.saveTraitsFile)
        self.fileMenu.addAction(saveTraitsButton)

        closeButton = QAction('Close', self)
        closeButton.setShortcut('Ctrl+W')
        closeButton.setShortcutContext(Qt.ApplicationShortcut)
        closeButton.setStatusTip('Close current file')
        closeButton.triggered.connect(self.closeFile)
        self.fileMenu.addAction(closeButton)
        
        exitButton = QAction('Quit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setShortcutContext(Qt.ApplicationShortcut)
        exitButton.setStatusTip('Quit application')
        exitButton.triggered.connect(self.quitApp)
        self.fileMenu.addAction(exitButton)
        
        self.editMenu = self.mainMenu.addMenu('Edit')
        
        undoButton = QAction('Undo', self)
        undoButton.setShortcut('Ctrl+Z')
        undoButton.setShortcutContext(Qt.ApplicationShortcut)
        undoButton.setStatusTip('Undo the last action')
        undoButton.triggered.connect(self.undo)
        self.editMenu.addAction(undoButton)
        
        redoButton = QAction('Redo', self)
        redoButton.setShortcut('Ctrl+Y')
        redoButton.setShortcutContext(Qt.ApplicationShortcut)
        redoButton.setStatusTip('Redo the last action')
        redoButton.triggered.connect(self.redo)
        self.editMenu.addAction(redoButton)

        self.modeMenu = self.mainMenu.addMenu('Mode')

        connectionModeButton = QAction('Connection', self)
        connectionModeButton.setShortcut('Ctrl+C')
        connectionModeButton.setShortcutContext(Qt.ApplicationShortcut)
        connectionModeButton.setStatusTip('Connect broken components')
        connectionModeButton.triggered.connect(self.enterConnectionMode)
        self.modeMenu.addAction(connectionModeButton)

        breakModeButton = QAction('Break', self)
        breakModeButton.setShortcut('Ctrl+B')
        breakModeButton.setShortcutContext(Qt.ApplicationShortcut)
        breakModeButton.setStatusTip('Break invalid edges')
        breakModeButton.triggered.connect(self.enterBreakMode)
        self.modeMenu.addAction(breakModeButton)

        splitModeButton = QAction('Split', self)
        splitModeButton.setShortcut('Ctrl+X')
        splitModeButton.setShortcutContext(Qt.ApplicationShortcut)
        splitModeButton.setStatusTip(
            'Split edges between two branches that have merged')
        splitModeButton.triggered.connect(self.enterSplitMode)
        self.modeMenu.addAction(splitModeButton)

        RemoveComponentButton = QAction('RemoveComponent', self)
        RemoveComponentButton.setShortcut('Ctrl+R')
        RemoveComponentButton.setShortcutContext(Qt.ApplicationShortcut)
        RemoveComponentButton.setStatusTip(
            'Remove entire component of selected edge')
        RemoveComponentButton.triggered.connect(self.enterRemoveComponentMode)
        self.modeMenu.addAction(RemoveComponentButton)

        SelectPriamryNodeButton = QAction('Primary Nodes', self)
        SelectPriamryNodeButton.setStatusTip('Select lists of primary nodes')
        SelectPriamryNodeButton.triggered.connect(
            self.enterSelectStemPrimaryNodeMode)
        self.modeMenu.addAction(SelectPriamryNodeButton)

        SelectPrimaryBranchesButton = QAction('Primary Edges', self)
        SelectPrimaryBranchesButton.setStatusTip(
            'Select lists of primary edges')
        SelectPrimaryBranchesButton.triggered.connect(
            self.enterSelectPrimaryBranchesMode)
        self.modeMenu.addAction(SelectPrimaryBranchesButton)

        self.viewMenu = self.mainMenu.addMenu('View Mode')

        viewGraphButton = QAction('MetaGraph', self)
        viewGraphButton.setShortcut('Ctrl+G')
        viewGraphButton.setShortcutContext(Qt.ApplicationShortcut)
        viewGraphButton.setStatusTip('View the metagpraph only')
        self.viewMenu.addAction(viewGraphButton)

        viewSkeletonButton = QAction('Skeleton', self)
        viewSkeletonButton.setShortcut('Ctrl+R')
        viewSkeletonButton.setShortcutContext(Qt.ApplicationShortcut)
        viewSkeletonButton.setStatusTip('View the skeleton only')
        self.viewMenu.addAction(viewSkeletonButton)

        viewBothButton = QAction('Both', self)
        viewBothButton.setShortcut('Ctrl+D')
        viewBothButton.setShortcutContext(Qt.ApplicationShortcut)
        viewBothButton.setStatusTip(
            'View metagraph and skeleton simultaneously')
        self.viewMenu.addAction(viewBothButton)

        recenterButton = QAction('Recenter', self)
        recenterButton.setShortcut('Ctrl+F')
        recenterButton.setShortcutContext(Qt.ApplicationShortcut)
        recenterButton.setStatusTip('Recenter view on skeleton')
        recenterButton.triggered.connect(self.glwidget.recenter)
        self.viewMenu.addAction(recenterButton)

        acceptShortcut = QAction('Accept Operation', self)
        acceptShortcut.setShortcut('Ctrl+A')
        acceptShortcut.setShortcutContext(Qt.ApplicationShortcut)
        acceptShortcut.triggered.connect(self.acceptPressed)
        self.addAction(acceptShortcut)

        centralWidget = QWidget()

        self.setCentralWidget(centralWidget)
        centralLayout = QGridLayout()
        centralLayout.addWidget(self.glwidget, 1, 1)
        centralWidget.setLayout(centralLayout)
        centralWidget.setSizePolicy(QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.glwidget.setSizePolicy(QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.glwidget.setMinimumSize(200, 200)

        w = 2880
        h = 1800
        self.resize(w, h)
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle('Skeleton Viewer')
        self.dockedWidget = None
        self.viewWidget = None

        self.createTabWidget(viewSkeletonButton, viewGraphButton, viewBothButton)

    def createTabWidget(self, viewSkeletonButton, viewGraphButton, viewBothButton):
        rightDock = QDockWidget('Editing', self)
        rightDock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.tabWidget = QTabWidget(rightDock)

        widget = QWidget(self.tabWidget)
        self.EditingTab = EditingTabWidget(self.glwidget.graph, widget)
        self.tabWidget.addTab(widget, 'Editing')
        self.EditingTab.modeChangeSig.connect(self.switchModes)

        widget = QWidget(self.tabWidget)
        self.TraitsTab = TraitsTabWidget(self.glwidget.graph, widget)
        self.tabWidget.addTab(widget, 'Traits')
        self.TraitsTab.modeChangeSig.connect(self.switchModes)
        self.TraitsTab.loadTraitsSig.connect(self.loadTraitsFile)
        self.TraitsTab.saveTraitsSig.connect(self.saveTraitsFile)

        rightDock.setWidget(self.tabWidget)
        label = QLabel('', rightDock)
        rightDock.setTitleBarWidget(label)
        self.addDockWidget(Qt.RightDockWidgetArea, rightDock)
        self.dockWidget = rightDock

        self.tabWidget.currentChanged.connect(self.tabChanged)

        leftDock = QDockWidget('Visualization', self)
        leftDock.setAllowedAreas(Qt.AllDockWidgetAreas)
        widget = QWidget(leftDock)
        self.VisualizationTab = VisualizationTabWidget(
            widget, self.glwidget.graph, viewSkeletonButton, viewGraphButton, viewBothButton)
        self.VisualizationTab.backgroundColorChanged.connect(
            self.glwidget.backgroundColorChanged)

        self.VisualizationTab.loadMeshSig.connect(self.loadMesh)

        leftDock.setWidget(widget)
        label = QLabel('', leftDock)
        leftDock.setTitleBarWidget(label)
        self.addDockWidget(Qt.LeftDockWidgetArea, leftDock)
        self.leftDockWidget = leftDock

    @pyqtSlot(int)
    def switchModes(self, mode: int):
        if self.currentMode != mode:
            self.currentMode = mode
            self.glwidget.currentMode = mode

    def enterConnectionMode(self):
        if self.currentMode == CONNECTION_MODE or self.currentMode == -2:
            return
        self.currentMode = CONNECTION_MODE
        self.tabWidget.setCurrentIndex(1)

    def enterBreakMode(self):
        if self.currentMode == BREAK_MODE or self.currentMode == -2:
            return
        self.currentMode = BREAK_MODE
        self.tabWidget.setCurrentIndex(2)

    def enterSplitMode(self):
        if self.currentMode == EDGE_SPLITTING_MODE or self.currentMode == -2:
            return
        self.currentMode = EDGE_SPLITTING_MODE
        self.tabWidget.setCurrentIndex(3)

    def enterRemoveComponentMode(self):
        if self.currentMode == COMPONENT_REMOVAL_MODE or self.currentMode == -2:
            return
        self.currentMode = COMPONENT_REMOVAL_MODE
        self.tabWidget.setCurrentIndex(4)

    def enterSelectStemMode(self):
        if self.currentMode == SELECT_STEM_MODE or self.currentMode == -2:
            return
        print("Enter select stem mode 903")
        self.currentMode = SELECT_STEM_MODE
        self.tabWidget.setCurrentIndex(SELECT_STEM_MODE)
        
    def enterSelectTopNodeMode(self):
        if self.currentMode == SELECT_TOP_NODE_MODE or self.currentMode == -2:
            return
        print("Enter select top node mode")
        self.currentMode = SELECT_TOP_NODE_MODE
        self.tabWidget.setCurrentIndex(SELECT_TOP_NODE_MODE)
        
    def enterSelectBottomNodeMode(self):
        if self.currentMode == SELECT_BOTTOM_NODE_MODE or self.currentMode == -2:
            return
        print("Enter select bottom node mode")
        self.currentMode = SELECT_BOTTOM_NODE_MODE
        self.tabWidget.setCurrentIndex(SELECT_BOTTOM_NODE_MODE)

    def enterSelectStemPrimaryNodeMode(self):
        if self.currentMode == SELECT_PRIMARY_NODES_MODE or self.currentMode == -2:
            return
        self.currentMode = SELECT_PRIMARY_NODES_MODE
        self.tabWidget.setCurrentIndex(7)

    def enterSelectPrimaryBranchesMode(self):
        if self.currentMode == -2:
            return
        print("Enter select primary edges mode")
        self.currentMode = SELECT_PRIMARY_BRANCHES_MODE
        self.tabWidget.setCurrentIndex(8)

    def eventFilter(self, obj, event):
        return False

    def closeDockWidget(self):
        print('closing dock widget')
        if self.dockedWidget != None:
            print('dock widget is not none')
            self.dockedWidget.hide()
            self.dockedWidget.destroy()

    def loadFile(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        self.loadFileName = QFileDialog.getOpenFileName(self, 'Open File', "")

        if self.loadFileName[0] != "":
            self.glwidget.loadFileEvent(str(self.loadFileName[0]))
            self.EditingTab.setGraph(self.glwidget.graph)
            self.TraitsTab.setGraph(self.glwidget.graph)
        
        self.VisualizationTab.edgeHeatmapChanged(DEFAULT_EDGE_HEATMAP_TYPE)
        self.VisualizationTab.nodeHeatmapChanged(DEFAULT_NODE_HEATMAP_TYPE)

    def loadMesh(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        meshFileName = QFileDialog.getOpenFileName(self, 'Open Mesh', "")

        if meshFileName != "":
            self.glwidget.graph.loadMeshFromFile(meshFileName[0])

    def saveFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.saveFileName = QFileDialog.getSaveFileName(
            self, 'Save File', filter="ply(*.ply)")

        if self.saveFileName[0] != "":
            self.glwidget.graph.saveToFile(self.saveFileName[0])
            
    def saveFairedSkeletonClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.saveFairedSkeletonName = QFileDialog.getSaveFileName(
            self, 'Save File', filter="ply(*.ply)")

        if self.saveFairedSkeletonName[0] != "":
            self.glwidget.graph.saveFairedSkeleton(self.saveFairedSkeletonName[0])

    def loadTraitsFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.loadFileName = QFileDialog.getOpenFileName(self, 'Open File', "")

        if self.loadFileName[0] != "":
            self.glwidget.loadTraitsFileEvent(str(self.loadFileName[0]))

    def saveTraitsFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.saveFileName = QFileDialog.getSaveFileName(
            self, 'Save File', filter="ply(*.ply)")

        if self.saveFileName[0] != "":
            self.glwidget.graph.saveTraitsToFile(self.saveFileName[0])
            
    def undo(self):
        pass
    
    def redo(self):
        pass
    
    def closeFile(self):
        choice = QMessageBox.question(self, 'Close', 'Close current file?', QMessageBox.Ok | QMessageBox.Cancel)
        if choice == QMessageBox.Ok:
            pass
        else:
            pass
    
    def quitApp(self):
        choice = QMessageBox.question(self, 'Quit', 'Quit application?', QMessageBox.Ok | QMessageBox.Cancel)
        if choice == QMessageBox.Ok:
            sys.exit()
        else:
            pass


def main():
    app = QApplication(sys.argv)
    window = RootsTabbedProgram()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
