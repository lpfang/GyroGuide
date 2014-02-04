from __main__ import vtk, qt, ctk, slicer
import numpy, time
#
# Puncture planner
#

class GyroGuide:
    def __init__(self, parent):
        parent.title = "GyroGuide"
        parent.categories = ["IGT"]
        parent.contributors = ["Ruifeng Chen, Luping Fang, Qing Pan (College of Information Engineering, Zhejiang University of Technology, Hangzhou, China);  Xiaolei Chen, Jiashu Zhang(Department of Neurosurgery, PLA General Hospital, Beijing, China)"]
        parent.helpText = "The module should be used in cooperation with Markups module. First, it is required to select five fiducial points to define two mutually-perpendicular planes as the Registration Markers. Second, set a target point and an entry point. Third, click the Calculate button to obtain the puncture path information, including the puncture depth and the angles between the puncture path and the reference planes.Finally, these resultsare displayed on a monitor or transmitted to the gyroscope-based device to assist the surgical operation."
        parent.acknowledgementText = "This work is supported by International Scientific and Technical Cooperation Project of Zhejiang Province(Grant 2012C34G2020027)"
        self.parent = parent
        
#
# PuncturePlanner Module Widget
#

class GyroGuideWidget:
    def __init__(self, parent = None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.markersFiducialsNodeSelector.setMRMLScene(slicer.mrmlScene)
            self.targetFiducialNodeSelector.setMRMLScene(slicer.mrmlScene)
            self.entryFiducialNodeSelector.setMRMLScene(slicer.mrmlScene)
            self.parent.show()

    def setup(self):
        # Puncture Planner collapsible button
        puncturePlannerCollapsibleButton = ctk.ctkCollapsibleButton()
        puncturePlannerCollapsibleButton.text = "Gyro Guide"
        self.layout.addWidget(puncturePlannerCollapsibleButton)

        #Layout within the puncture planner collapsible button
        puncturePlannerFormLayout = qt.QFormLayout(puncturePlannerCollapsibleButton)

        #Markers fiducials node selector
        markersFiducialsNodeSelector = slicer.qMRMLNodeComboBox()
        markersFiducialsNodeSelector.objectName = 'markersFiducialsNodeSelector'
        markersFiducialsNodeSelector.toolTip = "Select a fiducial list containing registration markers"
        markersFiducialsNodeSelector.nodeTypes = ['vtkMRMLMarkupsFiducialNode','vtkMRMLAnnotationHierarchyNode','vtkMRMLFiducialListNode']
        markersFiducialsNodeSelector.noneEnabled = True
        markersFiducialsNodeSelector.addEnabled = False
        markersFiducialsNodeSelector.removeEnabled = False
        markersFiducialsNodeSelector.connect('currentNodeChanged(bool)', self.enableOrDisableCalculateButton)
        puncturePlannerFormLayout.addRow("Markers", markersFiducialsNodeSelector)
        self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)', markersFiducialsNodeSelector, 'setMRMLScene(vtkMRMLScene*)')

        #Target Point fiducial node selector
        targetFiducialNodeSelector = slicer.qMRMLNodeComboBox()
        targetFiducialNodeSelector.objectName = 'targetFiducialNodeSelector'
        targetFiducialNodeSelector.toolTip = 'Select a fiducial list containing target point'
        targetFiducialNodeSelector.nodeTypes = ['vtkMRMLMarkupsFiducialNode','vtkMRMLAnnotationHierarchyNode','vtkMRMLFiducialListNode']
        targetFiducialNodeSelector.noneEnabled = True
        targetFiducialNodeSelector.addEnabled = False
        targetFiducialNodeSelector.removeEnabled = False
        targetFiducialNodeSelector.connect('currentNodeChanged(bool)', self.enableOrDisableCalculateButton)
        puncturePlannerFormLayout.addRow('Target Point', targetFiducialNodeSelector)
        self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)', targetFiducialNodeSelector, 'setMRMLScene(vtkMRMLScene*)')

        #Entry Point fiducial node selector
        entryFiducialNodeSelector = slicer.qMRMLNodeComboBox()
        entryFiducialNodeSelector.objectName = 'entryFiducialNodeSelector'
        entryFiducialNodeSelector.toolTip = 'Select a fiducial list containing entry point'
        entryFiducialNodeSelector.nodeTypes = ['vtkMRMLMarkupsFiducialNode','vtkMRMLAnnotationHierarchyNode','vtkMRMLFiducialListNode']
        entryFiducialNodeSelector.noneEnabled = True
        entryFiducialNodeSelector.addEnabled = False
        entryFiducialNodeSelector.removeEnabled = False
        entryFiducialNodeSelector.connect('currentNodeChanged(bool)', self.enableOrDisableCalculateButton)
        puncturePlannerFormLayout.addRow('Entry Point', entryFiducialNodeSelector)
        self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)', entryFiducialNodeSelector, 'setMRMLScene(vtkMRMLScene*)')

        #Calculate button
        calculateButton = qt.QPushButton("Calculate")
        calculateButton.toolTip = "Calculate the angles between the puncture path and the reference planes"
        calculateButton.enabled = False
        puncturePlannerFormLayout.addRow(calculateButton)
        calculateButton.connect('clicked()',self.onCalculateButtonClicked)

        #Results groupbox
        resultsGroupBox = qt.QGroupBox('Results')
        resultsVBoxLayout = qt.QVBoxLayout()
        
        #Angles Label
        anglesLabel = qt.QLabel('Angles between Puncture Path and')
        anglesReslutsFormLayout = qt.QFormLayout()
        
        angleResultRedPlaneLabel = qt.QLabel()
        angleResultRedPlaneLabel.setFrameStyle(qt.QFrame.Sunken | qt.QFrame.Panel)
        anglesReslutsFormLayout.addRow('   Red Plane : ', angleResultRedPlaneLabel)

        angleResultGreenPlaneLabel = qt.QLabel()
        angleResultGreenPlaneLabel.setFrameStyle(qt.QFrame.Sunken | qt.QFrame.Panel)
        anglesReslutsFormLayout.addRow('   Green Plane : ', angleResultGreenPlaneLabel)

        angleResultBluePlaneLabel = qt.QLabel()
        angleResultBluePlaneLabel.setFrameStyle(qt.QFrame.Sunken | qt.QFrame.Panel)
        anglesReslutsFormLayout.addRow('   Blue Plane : ', angleResultBluePlaneLabel)

        #Distance label
        distanceLabel = qt.QLabel('Distance between Target and Entry Point')
        distanceResultLabel = qt.QLabel()
        distanceResultLabel.setFrameStyle(qt.QFrame.Sunken | qt.QFrame.Panel)
        distanceReslutsFormLayout = qt.QFormLayout()
        distanceReslutsFormLayout.addRow('                 ', distanceResultLabel)

        resultsVBoxLayout.addWidget(anglesLabel)
        resultsVBoxLayout.addLayout(anglesReslutsFormLayout)
        resultsVBoxLayout.addWidget(distanceLabel)
        resultsVBoxLayout.addLayout(distanceReslutsFormLayout)

        resultsGroupBox.setLayout(resultsVBoxLayout)

        puncturePlannerFormLayout.addRow(resultsGroupBox)

        # Exporter collapsible button
        exporterCollapsibleButton = ctk.ctkCollapsibleButton()
        exporterCollapsibleButton.text = "Exporter"
        exporterCollapsibleButton.enabled = False
        self.layout.addWidget(exporterCollapsibleButton)

        #Layout within the exporter collapsible button
        exporterFormLayout = qt.QFormLayout(exporterCollapsibleButton)

        #Hostname and port label 
        hostportHBoxLayout = qt.QHBoxLayout()
        hostnameLabel = qt.QLabel('Hostname : ')
        hostnameLineEdit = qt.QLineEdit('localhost')
        portLabel = qt.QLabel('Port : ')
        portLineEdit = qt.QLineEdit('18944')
        hostportHBoxLayout.addWidget(hostnameLabel)
        hostportHBoxLayout.addWidget(hostnameLineEdit)
        hostportHBoxLayout.addWidget(portLabel)
        hostportHBoxLayout.addWidget(portLineEdit)

        exporterFormLayout.addRow(hostportHBoxLayout)

        #Send button
        sendButton = qt.QPushButton("Send")
        sendButton.toolTip = "Send the calculated parameters to external device which supports OpenIGTLink protocol"

        exporterFormLayout.addRow(sendButton)
        sendButton.connect('clicked()', self.onSendButtonClicked)

        #Add vertical spacer
        self.layout.addStretch(1)

        #Set local var as instance attribute
        self.markersFiducialsNodeSelector = markersFiducialsNodeSelector
        self.targetFiducialNodeSelector = targetFiducialNodeSelector
        self.entryFiducialNodeSelector = entryFiducialNodeSelector
        self.angleResultRedPlaneLabel = angleResultRedPlaneLabel
        self.angleResultGreenPlaneLabel = angleResultGreenPlaneLabel
        self.angleResultBluePlaneLabel = angleResultBluePlaneLabel
        self.distanceResultLabel = distanceResultLabel
        self.hostnameLineEdit = hostnameLineEdit
        self.portLineEdit = portLineEdit
        
        self.exporterCollapsibleButton = exporterCollapsibleButton
        self.calculateButton = calculateButton
        self.sendButton = sendButton

    def enableOrDisableCalculateButton(self):
        """Connected to the Markers, Target and Entry Point node selector. It allows to enable or disable the 'Calculate' button."""
        
        self.calculateButton.enabled = self.markersFiducialsNodeSelector.currentNode() != None and self.targetFiducialNodeSelector.currentNode() != None and self.entryFiducialNodeSelector.currentNode() != None

    def onCalculateButtonClicked(self):
        """ Connected to 'Calculate' button. It allows to :
              --- --- calculate the angles between puncture path and the reference plane ( PlaneRend, PlaneGreen, Plane Blue) and the distance between target and entry point."""
        
        markersFiducialsNode = self.markersFiducialsNodeSelector.currentNode()
        targetFiducialNode = self.targetFiducialNodeSelector.currentNode()
        entryFiducialNode = self.entryFiducialNodeSelector.currentNode()
        
        result = PuncturePlannerCalculator(markersFiducialsNode, targetFiducialNode, entryFiducialNode)

        model = PlaneLineModel(result)
        
        self.angleResultRedPlaneLabel.setText(result.angleRed)
        self.angleResultGreenPlaneLabel.setText(result.angleGreen)
        self.angleResultBluePlaneLabel.setText(result.angleBlue)
        self.distanceResultLabel.setText(str(result.distance) + ' mm')

        self.result = result
        self.exporterCollapsibleButton.enabled = True

    def onSendButtonClicked(self):
        """Send the data to the Extral Devices which support the OpenIGTLink protocal"""
        # Get the number of the 'vtkMRMLIGTLConnectorNode'
        n = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLIGTLConnectorNode')
        # Set the 'vtkMRMLIGTLConnectorNode' node
        if n > 0:
            for i in range(n):
                if slicer.mrmlScene.GetNthNodeByClass(i, 'vtkMRMLIGTLConnectorNode').GetName() == 'Send-Data':
                    connectorNode = slicer.mrmlScene.GetNthNodeByClass(i, 'vtkMRMLIGTLConnectorNode')
                else:
                    connectorNode = slicer.vtkMRMLIGTLConnectorNode()
                    slicer.mrmlScene.AddNode(connectorNode)
                    connectorNode.SetName('Send-Data')
        else:
            connectorNode = slicer.vtkMRMLIGTLConnectorNode()
            slicer.mrmlScene.AddNode(connectorNode)
            connectorNode.SetName('Send-Data')

        hostname = self.hostnameLineEdit.text
        port = int(self.portLineEdit.text)
        connectorNode.SetTypeClient(hostname, port)
        checker = connectorNode.Start()

        #Get the number of the 'vtkMRMLLinearTransformNode'
        n = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLLinearTransformNode')
        #Set the 'vtkMRMLLinearTransformNode' node
        nodes = []
        for i in range(n):
            nodes.append(slicer.mrmlScene.GetNthNodeByClass(i, 'vtkMRMLLinearTransformNode'))
        for i in range(n):
            if nodes[i].GetName() == 'Result-Data':
                slicer.mrmlScene.RemoveNode(nodes[i])
        transformNode = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(transformNode)
        transformNode.SetName('Result-Data')

        connectorNode.RegisterOutgoingMRMLNode(transformNode)
        matrix = transformNode.GetMatrixTransformToParent()
        theta = self.result.angleRed
        omega = self.result.angleGreen
        phi = self.result.angleBlue
        e1 = numpy.cos(phi)*numpy.cos(omega)
        e2 = numpy.sin(phi)*numpy.cos(theta) + numpy.cos(phi)*numpy.sin(omega)*numpy.sin(theta)
        e3 = numpy.sin(phi)*numpy.sin(theta) - numpy.cos(phi)*numpy.sin(omega)*numpy.cos(theta)
        e4 = self.result.distance

        e5 = numpy.sin(phi)*numpy.cos(omega)*(-1)
        e6 = numpy.cos(phi)*numpy.cos(theta) - numpy.sin(phi)*numpy.sin(omega)*numpy.sin(theta)
        e7 = numpy.cos(phi)*numpy.sin(theta) + numpy.sin(phi)*numpy.sin(omega)*numpy.cos(theta)
        e8 = 0

        e9 = numpy.sin(omega)
        e10 = numpy.cos(omega)*numpy.sin(theta)*(-1)
        e11 = numpy.cos(omega)*numpy.cos(theta)
        e12 = 0
        
        time.sleep(1)
        matrix.DeepCopy((e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12,0,0,0,1))
        time.sleep(1)
        connectorNode.Stop()       

class PuncturePlannerCalculator:
    """ Calculate the angles and distance with the given markers, target and entry point"""
    
    def __init__(self, markersFiducialsNode, targetFiducialNode, entryFiducialNode):
        
        self.fids = [markersFiducialsNode, targetFiducialNode, entryFiducialNode]

        # Get the point's coordinates in the markers, target and entry fiducials
        self.position = [] #save the points' position
        for i in range(len(self.fids)):
            if self.fids[i].GetClassName() == "vtkMRMLAnnotationHierarchyNode":
                # slicer4 style hierarchy nodes
                collection = vtk.vtkCollection()
                self.fids[i].GetChildrenDisplayableNodes(collection)
                self.n =  collection.GetNumberOfItems()
                if self.n == 0:
                    return
                self.p = numpy.zeros((self.n,3))
                for j in xrange(self.n):
                    f = collection.GetItemAsObject(j)
                    coords = [0,0,0]
                    f.GetFiducialCoordinates(coords)
                    self.p[j] = coords
            elif self.fids[i].GetClassName() == 'vtkMRMLMarkupsFiducialNode':
                # slicer4 Markups node
                self.n = self.fids[i].GetNumberOfFiducials()
                n = self.n
                if n == 0:
                    return
                # get fiducial positions
                # sets self.p
                self.p = numpy.zeros((n,3))
                for j in xrange(n):
                    coord = [0.0, 0.0, 0.0]
                    self.fids[i].GetNthFiducialPosition(j, coord)
                    self.p[j] = coord
            else:
                # slicer3 style fiducial lists
                self.n = self.fids[i].GetNumberOfFiducials()
                n = self.n
                if n == 0:
                    return
                #sets self.p
                self.p = numpy.zeros((n,3))
                for j in xrange(n):
                    self.p[j] = self.fids[i].GetNthFiducialXYZ(j)
            self.position.append(self.p)

        #Vectors of the points and the normals of the reference plane
        vector1 = self.position[0][0] - self.position[0][1] #a vector in the plane red
        vector2 = self.position[0][0] - self.position[0][2] #a vector in the plane red
        normalRed = numpy.cross(vector1,vector2) #normal of the plane red using the 'numpy.cross()' to calculate the cross product of two vector
        vector3 = self.position[0][3] - self.position[0][4] #a vector in the plane green
        normalGreen = numpy.cross(vector3, normalRed) #normal of the plane green
        normalBlue = numpy.cross(normalRed, normalGreen)#normal of the plane blue

        #Vector of the target and entry point
        vectorTargetEntry = self.position[1][0] - self.position[2][0]# the vector the target and entry point

        #Distance between target and entry point
        distance = round(numpy.linalg.norm(vectorTargetEntry), 1)

        #Angles between the puncture path and the reference plane
        sinAngleRed = numpy.abs(numpy.dot(vectorTargetEntry, normalRed)) / (numpy.linalg.norm(normalRed)*numpy.linalg.norm(vectorTargetEntry)) 
        sinAngleGreen = numpy.abs(numpy.dot(vectorTargetEntry, normalGreen)) / (numpy.linalg.norm(normalGreen)*numpy.linalg.norm(vectorTargetEntry)) 
        sinAngleBlue = numpy.abs(numpy.dot(vectorTargetEntry, normalBlue)) / (numpy.linalg.norm(normalBlue)*numpy.linalg.norm(vectorTargetEntry))

        angleRed = round(numpy.arcsin(sinAngleRed) / numpy.pi * 180.0, 1) # angle of the puncture path relative to the plane red
        angleGreen = round(numpy.arcsin(sinAngleGreen) / numpy.pi * 180.0, 1) # angle of the puncture path relative to the plane green
        angleBlue = round(numpy.arcsin(sinAngleBlue) / numpy.pi * 180.0, 1) # angle of the puncture path relative to the plane blue

        self.normalRed = normalRed
        self.normalGreen = normalGreen
        self.normalBlue = normalBlue
        
        self.angleRed = angleRed
        self.angleGreen = angleGreen
        self.angleBlue = angleBlue
        self.distance = distance

class PlaneLineModel:
    """ Create the reference planes and the puncture path """
    def __init__(self, dataset):
        
        # Markers, target and entry point
        markers = dataset.position[0]
        target = dataset.position[1][0]
        entry = dataset.position[2][0]
        
        # Normal of the reference plane
        normalRed = dataset.normalRed
        normalGreen = dataset.normalGreen
        normalBlue = dataset.normalBlue

        scene = slicer.mrmlScene
        n = scene.GetNumberOfNodesByClass('vtkMRMLModelNode')
        model = []
        modelName = []
        for i in range(n):
            model.append(scene.GetNthNodeByClass(i, 'vtkMRMLModelNode'))
            modelName.append(model[i].GetName())
        for i in range(len(model)):
            if modelName[i][0:5] == 'Plane' or modelName[i][0:8] == 'Puncture' or modelName[i][0:7] == 'Project' or modelName[i][0:4] == 'Line':
                scene.RemoveNode(model[i])

        #Reference plane model
        planeRed = self.planeModel(scene, normalRed, markers[0], 'Plane-Red',(1,0,0))
        planeGreen = self.planeModel(scene, normalGreen, markers[3], 'Plane-Green', (0,1,0))
        planeBlue = self.planeModel(scene, normalBlue, (0,0,0), 'Plane-Blue', (0,0,1))

        #Puncture path model
        puncturePath = self.lineModel(scene, target, entry, 'Puncture-Path',(0,1,1))

        #Compute the project points in reference planes
        projectPoints = numpy.zeros((6,3))
        planeRed.GeneralizedProjectPoint(target,projectPoints[0])
        planeRed.GeneralizedProjectPoint(entry, projectPoints[1])

        planeGreen.GeneralizedProjectPoint(target,projectPoints[2])
        planeGreen.GeneralizedProjectPoint(entry,projectPoints[3])
        
        planeBlue.GeneralizedProjectPoint(target,projectPoints[4])
        planeBlue.GeneralizedProjectPoint(entry,projectPoints[5])

        #Project points model
        planeDict = {0:'Red', 1:'Green', 2:'Blue'}
        for i in range(3):
            targetProject = self.pointModel(scene,projectPoints[i*2],'Project-Target-Point-' + planeDict[i],(1,1,0))
            entryProject = self.pointModel(scene, projectPoints[i*2+1], 'Project-Entry-Point-' + planeDict[i],(1,1,0))

        #The lines between the project points and the entry and target point
        for i in range(3):
            line1 = self.lineModel(scene, target, projectPoints[i*2], 'Line', (1,1,0))
            line2 = self.lineModel(scene, entry, projectPoints[i*2 + 1], 'Line', (1,1,0))

        for i in range(0, 6, 2):
            line3 = self.lineModel(scene, projectPoints[i], projectPoints[i+1], 'Line', (1,1,0))

    def planeModel(self, scene, normal, origin, name, color):
        """ Create a plane model node which can be viewed in the 3D View """
        
        #A plane source
        plane = vtk.vtkPlane()
        plane.SetOrigin(origin)
        plane.SetNormal(normal)
        
        planeSample = vtk.vtkSampleFunction()
        planeSample.SetImplicitFunction(plane)
        planeSample.SetModelBounds(-100,100,-100,100,-100,100)
        planeSample.SetSampleDimensions(100,100,100)
        planeSample.ComputeNormalsOff()
        planeContour = vtk.vtkContourFilter()
        planeContour.SetInput(planeSample.GetOutput())
        
        # Create plane model node
        planeNode = slicer.vtkMRMLModelNode()
        planeNode.SetScene(scene)
        planeNode.SetName(name)
        planeNode.SetAndObservePolyData(planeContour.GetOutput())
        
        # Create plane display model node
        planeModelDisplay = slicer.vtkMRMLModelDisplayNode()
        planeModelDisplay.SetColor(color)
        planeModelDisplay.SetBackfaceCulling(0)
        planeModelDisplay.SetScene(scene)
        scene.AddNode(planeModelDisplay)
        planeNode.SetAndObserveDisplayNodeID(planeModelDisplay.GetID())

        #Add to scene
        planeModelDisplay.SetInputPolyData(planeContour.GetOutput())
        scene.AddNode(planeNode)
        return plane

    def lineModel(self, scene, point1, point2, name, color):
        """ Create a line to reflect the puncture path"""
        #Line mode source
        line = vtk.vtkLineSource()
        line.SetPoint1(point1)#(point1[0][0], point1[0][1], point1[0][2])
        line.SetPoint2(point2)#(point2[0][0], point2[0][1], point2[0][2])
        
        # Create model node
        lineModel = slicer.vtkMRMLModelNode()
        lineModel.SetScene(scene)
        lineModel.SetName(name)
        lineModel.SetAndObservePolyData(line.GetOutput())

        # Create display node
        lineModelDisplay = slicer.vtkMRMLModelDisplayNode()
        lineModelDisplay.SetColor(color)
        lineModelDisplay.SetScene(scene)
        scene.AddNode(lineModelDisplay)
        lineModel.SetAndObserveDisplayNodeID(lineModelDisplay.GetID())

        #Add to scene
        lineModelDisplay.SetInputPolyData(line.GetOutput())
        scene.AddNode(lineModel)
        return line

    def pointModel(self, scene, point, name, color):
        """ Create a point model using sphere"""
        #Point 
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(point)
        sphere.SetRadius(2)
        # Create model node
        pointModel = slicer.vtkMRMLModelNode()
        pointModel.SetScene(scene)
        pointModel.SetName(name)
        pointModel.SetAndObservePolyData(sphere.GetOutput())
        #Create display node
        pointModelDisplay = slicer.vtkMRMLModelDisplayNode()
        pointModelDisplay.SetColor(color)
        pointModelDisplay.SetScene(scene)
        scene.AddNode(pointModelDisplay)
        pointModel.SetAndObserveDisplayNodeID(pointModelDisplay.GetID())
        #Add to scene
        pointModelDisplay.SetInputPolyData(sphere.GetOutput())
        scene.AddNode(pointModel)
