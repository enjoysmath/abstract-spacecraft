# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_text_dockwidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EditTextDockWidget(object):
    def setupUi(self, EditTextDockWidget):
        EditTextDockWidget.setObjectName("EditTextDockWidget")
        EditTextDockWidget.resize(185, 293)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.itemTypeTabs = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.itemTypeTabs.setTabPosition(QtWidgets.QTabWidget.North)
        self.itemTypeTabs.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.itemTypeTabs.setObjectName("itemTypeTabs")
        self.objectTab = QtWidgets.QWidget()
        self.objectTab.setObjectName("objectTab")
        self.itemTypeTabs.addTab(self.objectTab, "")
        self.arrowTab = QtWidgets.QWidget()
        self.arrowTab.setObjectName("arrowTab")
        self.itemTypeTabs.addTab(self.arrowTab, "")
        self.gridLayout.addWidget(self.itemTypeTabs, 1, 0, 1, 2)
        self.setSelectedButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.setSelectedButton.setObjectName("setSelectedButton")
        self.gridLayout.addWidget(self.setSelectedButton, 0, 0, 1, 1)
        self.unicodeShapeCatcherButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.unicodeShapeCatcherButton.setObjectName("unicodeShapeCatcherButton")
        self.gridLayout.addWidget(self.unicodeShapeCatcherButton, 0, 1, 1, 1)
        EditTextDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(EditTextDockWidget)
        self.itemTypeTabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(EditTextDockWidget)

    def retranslateUi(self, EditTextDockWidget):
        _translate = QtCore.QCoreApplication.translate
        EditTextDockWidget.setWindowTitle(_translate("EditTextDockWidget", "Edit Text"))
        self.itemTypeTabs.setTabText(self.itemTypeTabs.indexOf(self.objectTab), _translate("EditTextDockWidget", "Object"))
        self.itemTypeTabs.setTabText(self.itemTypeTabs.indexOf(self.arrowTab), _translate("EditTextDockWidget", "Arrow"))
        self.setSelectedButton.setText(_translate("EditTextDockWidget", "Set selected"))
        self.unicodeShapeCatcherButton.setText(_translate("EditTextDockWidget", "Symbol helper 🡕"))
import resources_rc
