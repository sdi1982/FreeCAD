# -*- coding: utf-8 -*-

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 sliptonic <shopinthewoods@gmail.com>               *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD
import FreeCADGui
import PathScripts.PathLog as PathLog
import PathScripts.PathOpGui as PathOpGui
import PathScripts.PathPocket as PathPocket
import PathScripts.PathSelection as PathSelection

from PySide import QtCore, QtGui

__title__ = "Path Pocket Base Operation UI"
__author__ = "sliptonic (Brad Collette)"
__url__ = "http://www.freecadweb.org"
__doc__ = "Base page controller and command implementation for path pocket operations."

def translate(context, text, disambig=None):
    return QtCore.QCoreApplication.translate(context, text, disambig)

FeaturePocket = 0x01
FeatureFacing = 0x02

class TaskPanelOpPage(PathOpGui.TaskPanelPage):
    '''Page controller class for pocket operations, supports two different features:
          FeaturePocket  ... used for pocketing operation
          FeatureFacing  ... used for face milling operation
    '''

    def pocketFeatures(self):
        '''pocketFeatures() ... return which features of the UI are supported by the operation.
        Typically one of the following is enabled:
          FeaturePocket  ... used for pocketing operation
          FeatureFacing  ... used for face milling operation
        Must be overwritten by subclasses'''
        pass

    def getForm(self):
        '''getForm() ... returns UI, adapted to the resutls from pocketFeatures()'''
        form = FreeCADGui.PySideUic.loadUi(":/panels/PageOpPocketFullEdit.ui")

        if not FeaturePocket & self.pocketFeatures():
            form.pocketWidget.hide()

        if not FeatureFacing & self.pocketFeatures():
            form.facingWidget.hide()

        return form

    def getFields(self, obj):
        '''getFields(obj) ... transfers values from UI to obj's proprties'''
        if obj.CutMode != str(self.form.cutMode.currentText()):
            obj.CutMode = str(self.form.cutMode.currentText())
        if obj.StepOver != self.form.stepOverPercent.value():
            obj.StepOver = self.form.stepOverPercent.value()
        if obj.OffsetPattern != str(self.form.offsetPattern.currentText()):
            obj.OffsetPattern = str(self.form.offsetPattern.currentText())
        self.updateInputField(obj, 'ZigZagAngle', self.form.zigZagAngle)

        self.updateToolController(obj, self.form.toolController)

        if FeaturePocket & self.pocketFeatures():
            self.updateInputField(obj, 'MaterialAllowance', self.form.extraOffset)
            if obj.UseStartPoint != self.form.useStartPoint.isChecked():
                obj.UseStartPoint = self.form.useStartPoint.isChecked()

        if FeatureFacing & self.pocketFeatures():
            self.updateInputField(obj, 'PassExtension', self.form.passExtension)
            if obj.BoundaryShape != str(self.form.boundaryShape.currentText()):
                obj.BoundaryShape = str(self.form.boundaryShape.currentText())

    def setFields(self, obj):
        '''setFields(obj) ... transfers obj's property values to UI'''
        self.form.zigZagAngle.setText(FreeCAD.Units.Quantity(obj.ZigZagAngle, FreeCAD.Units.Angle).UserString)
        self.form.stepOverPercent.setValue(obj.StepOver)

        self.selectInComboBox(obj.OffsetPattern, self.form.offsetPattern)
        self.selectInComboBox(obj.CutMode, self.form.cutMode)
        self.setupToolController(obj, self.form.toolController)

        if FeaturePocket & self.pocketFeatures():
            self.form.useStartPoint.setChecked(obj.UseStartPoint)
            self.form.extraOffset.setText(FreeCAD.Units.Quantity(obj.MaterialAllowance.Value, FreeCAD.Units.Length).UserString)

        if FeatureFacing & self.pocketFeatures():
            self.form.passExtension.setText(FreeCAD.Units.Quantity(obj.PassExtension.Value, FreeCAD.Units.Length).UserString)
            self.selectInComboBox(obj.BoundaryShape, self.form.boundaryShape)

    def getSignalsForUpdate(self, obj):
        '''getSignalsForUpdate(obj) ... return list of signals for updating obj'''
        signals = []

        signals.append(self.form.cutMode.currentIndexChanged)
        signals.append(self.form.offsetPattern.currentIndexChanged)
        signals.append(self.form.stepOverPercent.editingFinished)
        signals.append(self.form.zigZagAngle.editingFinished)
        signals.append(self.form.toolController.currentIndexChanged)

        if FeaturePocket & self.pocketFeatures():
            signals.append(self.form.extraOffset.editingFinished)
            signals.append(self.form.useStartPoint.clicked)

        if FeatureFacing & self.pocketFeatures():
            signals.append(self.form.boundaryShape.currentIndexChanged)
            signals.append(self.form.passExtension.editingFinished)

        return signals