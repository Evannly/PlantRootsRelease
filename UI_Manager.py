# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 02:48:14 2017

@author: Will
"""

# from RootsTool import Point3d, RootAttributes, Skeleton, mgraph
import sys
sys.path.append('E:/python')
from RootsTool import Point3d, RootAttributes, Skeleton, mgraph
#MetaNode3d, MetaEdge3d, MetaGraph,

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from PyQt5 import QtGui

import sys
from VisualizationTabWidget import Ui_VisualizationTabWidget
from EditingTabWidget import Ui_EditingTabWidget
from TraitsTabWidget import Ui_TraitsTabWidget
from SorghumTabWidget import Sorghum_Window
import matplotlib.cm as cm
import matplotlib.pyplot as plt

import test_glviewer as tgl
#from GLObjects import MetaGraphGL, Colorization

#from MetaGraphThread import MetaGraphThread
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import types
from tkinter import messagebox

NoMode = 0
ConnectionMode = 1
BreakMode = 2
SplitEdgeMode = 3
RemoveComponentMode = 4


SelectStemMode = 6
SelectPrimaryNodesMode = 7
SelectPrimaryBranchesMode = 8
SelectSegmentPointMode = 9

ViewNodeInfoMode = 10

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


from math import log10, floor
def round_to_2(x):
  return round(x, -int(floor(log10(abs(x)))) + 1)
  

    

class VisualizationTabWidget(Ui_VisualizationTabWidget, QObject):

    viewSkeleton = pyqtSignal(bool)
    viewGraph = pyqtSignal(bool)
    viewBoth = pyqtSignal(bool)

    backgroundColorChanged = pyqtSignal(float, float, float)
    loadMeshSig = pyqtSignal()

    def getHeatmap(self, idx : int): #idx is option of heatmap
        print("idx is ", idx)
        if idx == 0:
            return [[1.0, 0.0, 0.0, 1.0]]
			
        else:
            return getColorList(1000, cm.get_cmap(self.heatmapOptions[idx]))

    @pyqtSlot(int)
    def edgeColorizationChanged(self, optionId : int):
        if optionId == 0: #thickness
            self.graph.colorizeEdgesByThickness()
            pass
        elif optionId == 1: #width
            self.graph.colorizeEdgesByWidth()
            pass
        elif optionId == 2: #thickness / width
            self.graph.colorizeEdgesByRatio()
            pass
        elif optionId ==3 : #component
            self.graph.colorizeEdgesByComponent()
            pass


    @pyqtSlot(int)
    def nodeColorizationChanged(self, optionId : int):
        if optionId == 0: #thickness
            self.graph.colorizeNodesByThickness()
            pass
        elif optionId == 1: #width
            self.graph.colorizeNodesByWidth()
            pass
        elif optionId == 2: #degree
            self.graph.colorizeNodesByDegree()
            pass
        elif optionId == 3: #component
            self.graph.colorizeNodesByComponent()
            pass
        elif optionId == 4: #flat node color
            self.graph.colorizeNodesByConstantColor()
    @pyqtSlot(int)
    def nodeHeatmapChanged(self, optionId : int):
        heatmap = self.getHeatmap(optionId)
        self.graph.assignNodeHeatmap(heatmap)

    @pyqtSlot(int)
    def edgeHeatmapChanged(self, optionId : int):
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
    def showJunctionsPressed(self, showJunctions : bool):
        self.graph.showJunctions(showJunctions)

    @pyqtSlot(bool)
    def showEndpointsPressed(self, showEndpoints : bool):
        self.graph.showEndpoints(showEndpoints)

    @pyqtSlot(bool)
    def showEdgesPressed(self, showEdges : bool):
        self.graph.showEdges(showEdges)

    @pyqtSlot(bool)
    def magnifyNonBridgesPressed(self, magnifyNonBridges : bool):
        self.graph.magnifyNonBridges(magnifyNonBridges)

    @pyqtSlot(bool)
    def showOnlyNonBridgesPressed(self, showOnly : bool):
        self.graph.showOnlyNonBridges(showOnly)

    @pyqtSlot(bool)
    def backgroundColorClicked(self, active):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentBackground, self.widget)
        self.backgroundColorChanged.emit(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentBackground = pickedColor

    @pyqtSlot(bool)
    def constantNodeColorClicked(self, active):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentNodeColor, self.widget)
        self.graph.setConstantNodeColor(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentNodeColor = pickedColor

    @pyqtSlot(bool)
    def edgeSelectionColorClicked(self, active):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentEdgeSelectionColor, self.widget)
        self.graph.setEdgeSelectionColor(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentEdgeSelectionColor = pickedColor

    @pyqtSlot(bool)
    def loadMeshClicked(self, active : bool):
        self.loadMeshSig.emit()

    @pyqtSlot(bool)
    def meshColorClicked(self, active : bool):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentMeshColor, self.widget)
        self.graph.setMeshColor(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentMeshColor = pickedColor

    @pyqtSlot(bool)
    def displayMeshClicked(self, doShow : bool):
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

        self.graph.setConstantNodeColor(self.currentNodeColor.redF(), self.currentNodeColor.greenF(),
                                        self.currentNodeColor.blueF())
        self.graph.setEdgeSelectionColor(self.currentEdgeSelectionColor.redF(), self.currentEdgeSelectionColor.greenF(),
                                         self.currentEdgeSelectionColor.blueF())

        self.graph.setMeshColor(self.currentMeshColor.redF(), self.currentMeshColor.greenF(),
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

        self.edgeColorization.currentIndexChanged.connect(self.edgeColorizationChanged)
        self.nodeColorization.currentIndexChanged.connect(self.nodeColorizationChanged)
        self.edgeHeatmapType.currentIndexChanged.connect(self.edgeHeatmapChanged)
        self.nodeHeatmapType.currentIndexChanged.connect(self.nodeHeatmapChanged)

        self.edgeColorization.setCurrentIndex(1)
        self.nodeColorization.setCurrentIndex(1)
        self.edgeColorization.setCurrentIndex(0)
        self.nodeColorization.setCurrentIndex(0)

        self.showEndpoints.toggled.connect(self.showEndpointsPressed)
        self.showJunctions.toggled.connect(self.showJunctionsPressed)
        self.showEdges.toggled.connect(self.showEdgesPressed)
        self.magnifyNonBridges.toggled.connect(self.magnifyNonBridgesPressed)
        self.displayOnlyNonBridges.toggled.connect(self.showOnlyNonBridgesPressed)

        self.backgroundColor.clicked.connect(self.backgroundColorClicked)
        self.constantNodeColor.clicked.connect(self.constantNodeColorClicked)
        self.edgeSelectionColor.clicked.connect(self.edgeSelectionColorClicked)

        self.showEndpoints.setChecked(True)
        self.showJunctions.setChecked(True)
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
        self.edgeColorCeiling.sliderReleased.connect(self.edgeColorCeilingChanged)
        self.nodeColorFloor.sliderReleased.connect(self.nodeColorFloorChanged)
        self.nodeColorCeiling.sliderReleased.connect(self.nodeColorCeilingChanged)
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
    def showOnlySelected(self, doShow : bool):
        self.showSelected = doShow
        if self.mode == ConnectionMode:
            if self.graph != None:
                self.graph.setDisplayOnlySelectedComponents(self.showSelected)

    @pyqtSlot(int)
    def componentOneChanged(self, component : int):
        self.component1 = component
        if self.mode == ConnectionMode:
            if self.graph != None:
                self.graph.setComponent1(component)

    @pyqtSlot(int)
    def componentTwoChanged(self, component : int):
        self.component2 = component
        if self.mode == ConnectionMode:
            if self.graph != None:
                self.graph.setComponent2(component)

    @pyqtSlot(bool)
    def showBoundingBoxes(self, doShow : bool):
        self.showBoxes = doShow
        if self.mode == ConnectionMode:
            if self.graph != None:
                self.graph.setShowBoundingBoxes(self.showBoxes)

    @pyqtSlot(bool)
    def connectionModePressed(self, pressed : bool):
        self.changeMode(ConnectionMode)

    @pyqtSlot(bool)
    def acceptConnectionPressed(self, pressed : bool):
        if self.mode == ConnectionMode:
            self.graph.joinOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def breakModePressed(self, pressed : bool):
        self.changeMode(BreakMode)
    @pyqtSlot(bool)
    def removeComponentPressed(self, pressed: bool):
        self.changeMode(RemoveComponentMode)

    @pyqtSlot(bool)
    def splitEdgeModePressed(self, pressed : bool):
        self.changeMode(SplitEdgeMode)


    @pyqtSlot(bool)
    def acceptRemovalPressed(self, pressed : bool):
        if self.mode == BreakMode:
            if self.graph != None:
                self.graph.breakOperation()
                self.updateWidget()
        if self.mode == SplitEdgeMode:
            if self.graph != None:
                self.graph.splitOperation()
                self.updateWidget()
        # add code to c++
        if self.mode == RemoveComponentMode:
            if self.graph != None:
                print('enter c++ for remove component')
                self.graph.removeComponentOperation()
                self.updateWidget()

    def __init__(self, graphObject : mgraph, widget=None):
        Ui_EditingTabWidget.__init__(self)
        QObject.__init__(self)
        self.setupUi(widget)
        self.widget = widget
        self.graph = graphObject
        self.showSelected = False
        self.showBoxes = False
        self.mode = NoMode
        self.component1 = 0
        self.component2 = 0

        self.showOnlySelectedButton.toggled.connect(self.showOnlySelected)
        self.showBoundingBoxesButton.toggled.connect(self.showBoundingBoxes)
        self.ComponentOne.currentIndexChanged.connect(self.componentOneChanged)
        self.ComponentTwo.currentIndexChanged.connect(self.componentTwoChanged)
        self.ConnectionModeButton.clicked.connect(self.connectionModePressed)
        self.AcceptConnectionButton.clicked.connect(self.acceptConnectionPressed)
        self.BreakModeButton.clicked.connect(self.breakModePressed)
        self.SplitModeButton.clicked.connect(self.splitEdgeModePressed)
        self.AcceptRemovalButton.clicked.connect(self.acceptRemovalPressed)
        self.RemoveComponentButton.clicked.connect(self.removeComponentPressed)


    def changeMode(self, mode : int):
        if self.mode != mode or mode > 5:
            self.mode = mode
            print("changing mode")
            if self.graph != None:
                self.graph.unselectAll()
                self.updateWidget()
                if mode != ConnectionMode:
                    self.graph.setDisplayOnlySelectedComponents(False)
                    self.graph.setShowBoundingBoxes(False)
                if mode == ConnectionMode:
                    self.graph.setDisplayOnlySelectedComponents(self.showSelected)
                    self.graph.setShowBoundingBoxes(self.showBoxes)
                self.graph.setDisplayStem(False)
                self.graph.setDisplayPrimaryNodes(False)
            self.modeChangeSig.emit(self.mode)

    def exitCurrentMode(self):
        pass

    def setGraph(self, graph : mgraph):
        print("setting graph")
        self.graph = graph
        self.updateWidget()
        if self.mode == ConnectionMode and self.graph != None:
            self.graph.setDisplayOnlySelectedComponents(self.showSelected)
            self.graph.setShowBoundingBoxes(self.showBoxes)


    def updateWidget(self):
        if self.graph != None:
            edgesString = str(self.graph.getNumEdgesToBreak())
            self.edgesToBreak.setText(edgesString)

            self.ComponentOne.currentIndexChanged.disconnect(self.componentOneChanged)
            self.ComponentTwo.currentIndexChanged.disconnect(self.componentTwoChanged)

            self.ComponentOne.clear()
            self.ComponentTwo.clear()
        
            componentSizes = self.graph.getComponentSizes()
            numComponents = self.graph.getNumComponents()
            for i in range(0, numComponents):
                descriptor = str(i) + ' - ' + str(round_to_2(componentSizes[i]))
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
        
            self.ComponentOne.currentIndexChanged.connect(self.componentOneChanged)
            self.ComponentTwo.currentIndexChanged.connect(self.componentTwoChanged)

        else:
            self.edgesToBreak.setText("")
            self.ComponentOne.clear()
            self.ComponentTwo.clear()
class SorghumTabWidget(Sorghum_Window,QObject):
    modeChangeSig = pyqtSignal(int)
    def __init__(self,graphObject: mgraph,widget=None):
        Ui_TraitsTabWidget.__init__(self)
        QObject.__init__(self)
        self.setupUi(widget)
        self.widget = widget
        self.graph = graphObject
        
class TraitsTabWidget(Ui_TraitsTabWidget, QObject):
    modeChangeSig = pyqtSignal(int)
    loadTraitsSig = pyqtSignal()
    saveTraitsSig = pyqtSignal()

    @pyqtSlot(bool)
    def loadTraitsPressed(self, pressed : bool):
        self.changeMode(SelectPrimaryBranchesMode)
        self.loadTraitsSig.emit()
        self.updateWidget()

    @pyqtSlot(bool)
    def saveTraitsPressed(self, pressed : bool):
        self.saveTraitsSig.emit()

    @pyqtSlot(bool)
    def showStemChecked(self, doShow : bool):
        self.showStem = doShow
        if self.graph != None:
                self.graph.setDisplayStem(self.showStem)

    @pyqtSlot(bool)
    def selectStemPressed(self, pressed : bool):
        self.changeMode(SelectStemMode)

    @pyqtSlot(bool)
    def confirmStemPressed(self, pressed : bool):
        if self.mode == SelectStemMode and self.graph:
            self.graph.selectStemOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def ViewNodeInfoPressed(self, pressed : bool):
        self.changeMode(ViewNodeInfoMode)

    @pyqtSlot(bool)
    def showStemSuggestionChecked(self, doShow : bool):
        if self.graph != None:
            self.graph.setDisplaySuggestedStem(doShow)

    @pyqtSlot(bool)
    def FindStemPressed(self, pressed : bool):
        # self.stemLowThreshold = float(self.LowThresholdLineEdit.text())
        try:
            self.stemLowThreshold = float(self.LowThresholdLineEdit.text())
        except ValueError:
            self.stemLowThreshold = int(self.LowThresholdLineEdit.text())
        # print(self.stemLowThreshold)
        if self.graph != None:
            self.graph.FindStemOperation(self.stemLowThreshold)
            self.updateWidget()

    @pyqtSlot(bool)
    def FindPrimaryNodePressed(self, Pressed : bool):
        try:
            self.nodeNeighbourRange = float(self.NodeIntervalLineEdit.text())
        except ValueError:
            self.nodeNeighbourRange = int(self.NodeIntervalLineEdit.text())

        try:
            self.Kernel_bandWidth = float(self.BandWidthLineEdit.text())
        except ValueError:
            self.Kernel_bandWidth = int(self.BandWidthLineEdit.text())

        if self.graph != None:
            self.graph.FindPrimaryNodeOperation(self.nodeNeighbourRange, self.Kernel_bandWidth)
            self.updateWidget()

    @pyqtSlot(bool)
    def showNodeSuggestionChecked(self, doShow : bool):
        if self.graph != None:
            self.graph.setDisplaySuggestedNode(doShow)

    @pyqtSlot(bool)
    def showPrimaryNodesChecked(self, doShow : bool):
        self.showPrimaryNodes = doShow
        if self.graph != None:
            self.graph.setDisplayPrimaryNodes(self.showPrimaryNodes)

    @pyqtSlot(bool)
    def randomColorizePrimaryNodesChecked(self, pressed : bool):
        self.isRandomColorizePrimaryNodes = pressed
        if self.graph != None:
            self.graph.setRandomColorizePrimaryNodes(self.isRandomColorizePrimaryNodes)
            self.updateWidget()

    @pyqtSlot(bool)
    def selectStemPrimaryNodePressed(self, pressed : bool):
        self.changeMode(SelectPrimaryNodesMode)

    @pyqtSlot(bool)
    def confirmPrimaryNodesPressed(self, pressed : bool):
        if self.mode == SelectPrimaryNodesMode and self.graph:
            self.graph.selectStemPrimaryNodeOperation()
            self.updateWidget()

    @pyqtSlot(int)
    def currentPrimaryNodeChanged(self, node : int):
        self.currentPrimaryNode = node
        if self.graph != None:
            self.graph.setCurrentPrimaryNode(self.currentPrimaryNode)

    @pyqtSlot(bool)
    def selectPrimaryBranchesPressed(self, pressed : bool):
        self.changeMode(SelectPrimaryBranchesMode)

    @pyqtSlot(bool)
    def confirmPrimaryBranchesPressed(self, pressed : bool):
        if self.mode == SelectPrimaryBranchesMode and self.graph:
            self.graph.selectPrimaryBranchesOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def removePrimaryBranchesPressed(self, pressed: bool):
        if self.mode == SelectPrimaryBranchesMode and self.graph:
            self.graph.RemovePrimaryBranchesOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def PrimaryNodeSelectionColorPressed(self, active):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentPrimaryNodeSelectionColor, self.widget)
        self.graph.setCurrentPrimaryNodeSelectionColor(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentPrimaryNodeSelectionColor = pickedColor

    @pyqtSlot(bool)
    def showConfirmedPrimaryBranchesChecked(self, doShow : bool):
        self.showConfirmedPrimaryBranches = doShow
        if self.mode == SelectPrimaryBranchesMode:
            if self.graph != None:
                self.graph.setDisplayConfirmedPrimaryBranches(self.showConfirmedPrimaryBranches)

    @pyqtSlot(bool)
    def showOnlyBranchesOfCurrentPrimaryNodeChecked(self, doShow : bool):
        self.showOnlyBranchesOfCurrentPrimaryNode = doShow
        if self.mode == SelectPrimaryBranchesMode and self.graph != None:
            self.graph.setDisplayOnlyBranchesOfCurrentPrimaryNode(self.showOnlyBranchesOfCurrentPrimaryNode)

    @pyqtSlot(bool)
    def showTraitsOnlyChecked(self, doShow : bool):
        self.showTraitsOnly = doShow
        if self.graph != None:
            self.graph.setDisplayTraitsOnly(self.showTraitsOnly)

    @pyqtSlot(bool)
    def SelectSegmentPointPressed(self, pressed : bool):
        self.changeMode(SelectSegmentPointMode)

    @pyqtSlot(bool)
    def ConfirmSegmentPointPressed(self):
        if self.mode == SelectSegmentPointMode and self.graph:
            self.graph.selectSegmentPointOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def showSelectedSegmentChecked(self, doShow : bool):
        self.showSelectedSegment = doShow
        if self.graph != None:
            self.graph.setDisplaySelectedSegment(self.showSelectedSegment)

    @pyqtSlot()
    def horizontalSliderRadiusChanged(self):
        sliderVal = self.horizontalSliderRadius.value()
        # floor = 1.0 * sliderVal / 100.0
        if not self.horizontalSliderRadius.isSliderDown():
            self.graph.setSegmentHorizontalSliderRadius(sliderVal)

    def __init__(self, graphObject: mgraph, widget=None):
        Ui_TraitsTabWidget.__init__(self)
        QObject.__init__(self)
        self.setupUi(widget)
        self.widget = widget
        self.graph = graphObject
        self.mode = NoMode
        self.showStem = False
        self.showPrimaryNodes = False
        self.currentPrimaryNode = 0
        self.showConfirmedPrimaryBranches = False
        self.isRandomColorizePrimaryNodes = False
        self.showOnlyBranchesOfCurrentPrimaryNode = False
        self.showSelectedSegment = False
        self.showTraitsOnly = False

        self.stemLowThreshold = 0
        self.nodeNeighbourRange = 0
        self.Kernel_bandWidth = 0

        self.currentPrimaryNodeSelectionColor = QColor(255, 255, 255)
        self.graph.setCurrentPrimaryNodeSelectionColor(self.currentPrimaryNodeSelectionColor.redF(),
                                                       self.currentPrimaryNodeSelectionColor.greenF(),
                                                       self.currentPrimaryNodeSelectionColor.blueF())

        self.loadTraitsButton.clicked.connect(self.loadTraitsPressed)
        self.saveTraitsButton.clicked.connect(self.saveTraitsPressed)

        # manual find stem
        # self.AcceptTraitSelectionButton.clicked.connect(self.acceptTraitSelectionPressed)
        self.showStemCheck.toggled.connect(self.showStemChecked)
        self.SelectStemButton.clicked.connect(self.selectStemPressed)
        self.ConfirmStemButton.clicked.connect(self.confirmStemPressed)
        # automatic find stem
        self.ViewNodeInfoButton.clicked.connect(self.ViewNodeInfoPressed)
        self.showStemSuggestionCheck.toggled.connect(self.showStemSuggestionChecked)
        self.FindStemButton.clicked.connect(self.FindStemPressed)

        # manual find primary nodes
        self.showPrimaryNodesCheck.toggled.connect(self.showPrimaryNodesChecked)
        self.SelectPriamryNodeButton.clicked.connect(self.selectStemPrimaryNodePressed)
        self.ConfirmPrimaryNodesButton.clicked.connect(self.confirmPrimaryNodesPressed)
        # automatic find primary nodes
        self.showNodeSuggestionCheck.toggled.connect(self.showNodeSuggestionChecked)
        self.FindPrimaryNodesButton.clicked.connect(self.FindPrimaryNodePressed)

        self.PrimaryNodeSelectionColorButton.clicked.connect(self.PrimaryNodeSelectionColorPressed)
        self.RandomColorizePrimaryNodesCheck.toggled.connect(self.randomColorizePrimaryNodesChecked)

        self.CurrentPrimaryNodeCombo.currentIndexChanged.connect(self.currentPrimaryNodeChanged)
        self.SelectPrimaryBranchesButton.clicked.connect(self.selectPrimaryBranchesPressed)
        self.ConfirmPrimaryBranchesButton.clicked.connect(self.confirmPrimaryBranchesPressed)
        self.RemovePrimaryBranchesButton.clicked.connect(self.removePrimaryBranchesPressed)
        self.showConfirmedPrimaryBranchesCheck.toggled.connect(self.showConfirmedPrimaryBranchesChecked)
        self.showOnlyBranchesOfCurrentPrimaryNodeCheck.toggled.connect(self.showOnlyBranchesOfCurrentPrimaryNodeChecked)
        self.showTraitsOnlyCheck.toggled.connect(self.showTraitsOnlyChecked)

        self.SelectSegmentPointButton.clicked.connect(self.SelectSegmentPointPressed)
        self.ConfirmSegmentPointButton.clicked.connect(self.ConfirmSegmentPointPressed)
        self.showSelectedSegmentCheck.toggled.connect(self.showSelectedSegmentChecked)

        self.horizontalSliderRadius.sliderReleased.connect(self.horizontalSliderRadiusChanged)
        self.horizontalSliderRadius.setSliderDown(True)
        self.horizontalSliderRadius.setValue(10)
        self.horizontalSliderRadius.setSliderDown(False)

    def changeMode(self, mode : int):
        if self.mode != mode or mode < 6:
            self.mode = mode
            print("changing mode")
            if self.graph != None:
                self.graph.unselectAll()
                self.updateWidget()
                if mode != ConnectionMode:
                    self.graph.setDisplayOnlySelectedComponents(False)
                    self.graph.setShowBoundingBoxes(False)
                if mode == ConnectionMode:
                    self.graph.setDisplayOnlySelectedComponents(self.showSelected)
                    self.graph.setShowBoundingBoxes(self.showBoxes)
                if mode != ConnectionMode and mode != SplitEdgeMode \
                        and mode != BreakMode \
                        and mode != RemoveComponentMode:
                    self.graph.setDisplayStem(self.showStem)
                    self.graph.setDisplayPrimaryNodes(self.showPrimaryNodes)
                else:
                    self.graph.setDisplayStem(False)
                    self.graph.setDisplayPrimaryNodes(False)
            self.modeChangeSig.emit(self.mode)

    def exitCurrentMode(self):
        pass

    def setGraph(self, graph : mgraph):
        print("setting graph")
        self.graph = graph
        self.updateWidget()
        if self.graph != None:
            if self.mode != ConnectionMode and self.mode != SplitEdgeMode \
                    and self.mode != BreakMode \
                    and self.mode != RemoveComponentMode:
                self.graph.setDisplayStem(self.showStem)
                self.graph.setDisplayPrimaryNodes(self.showPrimaryNodes)
            else:
                self.graph.setDisplayStem(False)
                self.graph.setDisplayPrimaryNodes(False)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def updateWidget(self):
        if self.graph != None:
            # update current primary node combo
            self.CurrentPrimaryNodeCombo.currentIndexChanged.disconnect(self.currentPrimaryNodeChanged)
            self.CurrentPrimaryNodeCombo.clear()
            numPrimaryNodes = self.graph.getNumPrimaryNodes()
            if numPrimaryNodes > 0:
                for i in range(0, numPrimaryNodes):
                    descriptor = str(i)
                    self.CurrentPrimaryNodeCombo.addItem(descriptor)
            else:
                self.CurrentPrimaryNodeCombo.clear()

            self.currentPrimaryNode = max(self.currentPrimaryNode, 0)
            self.currentPrimaryNode = min(self.currentPrimaryNode, numPrimaryNodes - 1)

            self.CurrentPrimaryNodeCombo.setCurrentIndex(self.currentPrimaryNode)
            self.graph.setCurrentPrimaryNode(self.currentPrimaryNode)
            self.CurrentPrimaryNodeCombo.currentIndexChanged.connect(self.currentPrimaryNodeChanged)

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
    def mainPrint(self, toPrint : object):
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
		#load root file
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

        loadTraitsButton = QAction('Load traits', self)
        loadTraitsButton.triggered.connect(self.loadTraitsFile)
        self.fileMenu.addAction(loadTraitsButton)

        saveTraitsButton = QAction('Save traits', self)
        saveTraitsButton.setShortcut('Ctrl+A')
        saveTraitsButton.setShortcutContext(Qt.ApplicationShortcut)
        saveTraitsButton.setStatusTip('Save traits')
        saveTraitsButton.triggered.connect(self.saveTraitsFile)
        self.fileMenu.addAction(saveTraitsButton)
        
        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+E')
        exitButton.setShortcutContext(Qt.ApplicationShortcut)
        exitButton.setStatusTip('Exit RootsEditor')
        exitButton.triggered.connect(self.close)
        self.fileMenu.addAction(exitButton)
        
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
        splitModeButton.setStatusTip('Split edges between two branches that have merged')
        splitModeButton.triggered.connect(self.enterSplitMode)
        self.modeMenu.addAction(splitModeButton)

        RemoveComponentButton = QAction('RemoveComponent', self)
        RemoveComponentButton.setShortcut('Ctrl+R')
        RemoveComponentButton.setShortcutContext(Qt.ApplicationShortcut)
        RemoveComponentButton.setStatusTip('Remove entire component of selected edge')
        RemoveComponentButton.triggered.connect(self.enterRemoveComponentMode)
        self.modeMenu.addAction(RemoveComponentButton)

        SelectStemButton = QAction('Stem', self)
        SelectStemButton.setShortcut('Ctrl+Shift+S')
        SelectStemButton.setShortcutContext(Qt.ApplicationShortcut)
        SelectStemButton.setStatusTip('Select two end node of a stem')
        SelectStemButton.triggered.connect(self.enterSelectStemMode)
        self.modeMenu.addAction(SelectStemButton)

        SelectPriamryNodeButton = QAction('Primary Nodes', self)
        SelectPriamryNodeButton.setStatusTip('Select lists of primary nodes')
        SelectPriamryNodeButton.triggered.connect(self.enterSelectStemPrimaryNodeMode)
        self.modeMenu.addAction(SelectPriamryNodeButton)

        SelectPrimaryBranchesButton = QAction('Primary Edges', self)
        SelectPrimaryBranchesButton.setStatusTip('Select lists of primary edges')
        SelectPrimaryBranchesButton.triggered.connect(self.enterSelectPrimaryBranchesMode)
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
        viewBothButton.setStatusTip('View metagraph and skeleton simultaneously')
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
        

        centralWidget = QtWidgets.QWidget()

        self.setCentralWidget(centralWidget)
        centralLayout = QtWidgets.QGridLayout()
        centralLayout.addWidget(self.glwidget, 1, 1)
        centralWidget.setLayout(centralLayout)
        centralWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.glwidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.glwidget.setMinimumSize(200, 200)
        
        
        w = 1800
        h = 1000
        self.resize(w, h)
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle('Skeleton Viewer')
        self.dockedWidget = None
        self.viewWidget = None
        
        self.createTabWidget(viewSkeletonButton, viewGraphButton, viewBothButton)
        
    def createTabWidget(self, viewSkeletonButton, viewGraphButton, viewBothButton):
        
        rightDock = QDockWidget('Editing', self)
        rightDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.tabWidget = QTabWidget(rightDock)
        
        widget = QtWidgets.QWidget(self.tabWidget)
        self.EditingTab = EditingTabWidget(self.glwidget.graph, widget)
        self.tabWidget.addTab(widget, 'Editing')
        self.EditingTab.modeChangeSig.connect(self.switchModes)

        widget = QtWidgets.QWidget(self.tabWidget)
        self.TraitsTab = TraitsTabWidget(self.glwidget.graph, widget)
        self.tabWidget.addTab(widget, 'Traits')
        self.TraitsTab.modeChangeSig.connect(self.switchModes)
        self.TraitsTab.loadTraitsSig.connect(self.loadTraitsFile)
        self.TraitsTab.saveTraitsSig.connect(self.saveTraitsFile)
        
        widget = QtWidgets.QWidget(self.tabWidget)
        self.SorghumTab = SorghumTabWidget(self.glwidget.graph,widget)
        self.tabWidget.addTab(widget,'Sorghum')
        self.TraitsTab.modeChangeSig.connect(self.switchModes)
        rightDock.setWidget(self.tabWidget)
        
        label = QtWidgets.QLabel('', rightDock)
        rightDock.setTitleBarWidget(label)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, rightDock)
        self.dockWidget = rightDock

        self.tabWidget.currentChanged.connect(self.tabChanged)

        leftDock = QDockWidget('Visualization', self)
        leftDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        widget = QtWidgets.QWidget(leftDock)
        self.VisualizationTab = VisualizationTabWidget(widget, self.glwidget.graph, viewSkeletonButton, viewGraphButton, viewBothButton)
        self.VisualizationTab.backgroundColorChanged.connect(self.glwidget.backgroundColorChanged)

        self.VisualizationTab.loadMeshSig.connect(self.loadMesh)

        leftDock.setWidget(widget)
        label = QtWidgets.QLabel('', leftDock)
        leftDock.setTitleBarWidget(label)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, leftDock)
        self.leftDockWidget = leftDock

    @pyqtSlot(int)
    def switchModes(self, mode : int):
        if self.currentMode != mode:
            self.currentMode = mode
            self.glwidget.currentMode = mode

    def enterConnectionMode(self):
        if self.currentMode == ConnectionMode or self.currentMode == -2:
            return
        self.currentMode = ConnectionMode
        self.tabWidget.setCurrentIndex(1)

    
    def enterBreakMode(self):
        if self.currentMode == BreakMode or self.currentMode == -2:
            return
        self.currentMode = BreakMode
        self.tabWidget.setCurrentIndex(2)
        
    def enterSplitMode(self):
        if self.currentMode == SplitEdgeMode or self.currentMode == -2:
            return
        self.currentMode = SplitEdgeMode
        self.tabWidget.setCurrentIndex(3)

    def enterRemoveComponentMode(self):
        if self.currentMode == RemoveComponentMode or self.currentMode == -2:
            return
        self.currentMode = RemoveComponentMode
        self.tabWidget.setCurrentIndex(4)

    def enterSelectStemMode(self):
        if self.currentMode == SelectStemMode or self.currentMode == -2:
            return
        print("Enter select stem mode 903")
        self.currentMode = SelectStemMode
        self.tabWidget.setCurrentIndex(6)

    def enterSelectStemPrimaryNodeMode(self):
        if self.currentMode == SelectPrimaryNodesMode or self.currentMode == -2:
            return
        self.currentMode = SelectPrimaryNodesMode
        self.tabWidget.setCurrentIndex(7)

    def enterSelectPrimaryBranchesMode(self):
        if self.currentMode == -2:
            return
        print("Enter select primary edges mode")
        self.currentMode = SelectPrimaryBranchesMode
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

    def loadMesh(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        meshFileName = QFileDialog.getOpenFileName(self, 'Open Mesh', "")

        if meshFileName != "":
            self.glwidget.graph.loadMeshFromFile(meshFileName[0])

    def saveFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.saveFileName = QFileDialog.getSaveFileName(self, 'Save File', filter="ply(*.ply)")

        if self.saveFileName[0] != "":
            self.glwidget.graph.saveToFile(self.saveFileName[0])

    def loadTraitsFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.loadFileName = QFileDialog.getOpenFileName(self, 'Open File', "")

        if self.loadFileName[0] != "":
            self.glwidget.loadTraitsFileEvent(str(self.loadFileName[0]))


    def saveTraitsFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.saveFileName = QFileDialog.getSaveFileName(self, 'Save File', filter="ply(*.ply)")

        if self.saveFileName[0] != "":
            self.glwidget.graph.saveTraitsToFile(self.saveFileName[0])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RootsTabbedProgram()
    window.show()
    sys.exit(app.exec_())
