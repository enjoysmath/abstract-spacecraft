# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'external_link_listing.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExternalLinkListing(object):
    def setupUi(self, ExternalLinkListing):
        ExternalLinkListing.setObjectName("ExternalLinkListing")
        ExternalLinkListing.resize(347, 81)
        self.gridLayout = QtWidgets.QGridLayout(ExternalLinkListing)
        self.gridLayout.setObjectName("gridLayout")
        self.externalLinkLabel = QtWidgets.QLabel(ExternalLinkListing)
        self.externalLinkLabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.externalLinkLabel.setFrameShadow(QtWidgets.QFrame.Plain)
        self.externalLinkLabel.setMidLineWidth(0)
        self.externalLinkLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.externalLinkLabel.setObjectName("externalLinkLabel")
        self.gridLayout.addWidget(self.externalLinkLabel, 0, 0, 1, 1)
        self.removeButton = QtWidgets.QPushButton(ExternalLinkListing)
        self.removeButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.removeButton.setObjectName("removeButton")
        self.gridLayout.addWidget(self.removeButton, 0, 1, 1, 1)

        self.retranslateUi(ExternalLinkListing)
        QtCore.QMetaObject.connectSlotsByName(ExternalLinkListing)

    def retranslateUi(self, ExternalLinkListing):
        _translate = QtCore.QCoreApplication.translate
        ExternalLinkListing.setWindowTitle(_translate("ExternalLinkListing", "Form"))
        self.externalLinkLabel.setText(_translate("ExternalLinkListing", "<a href=\"https://www.google.com\">Link 🔗</a>"))
        self.removeButton.setText(_translate("ExternalLinkListing", "❌"))
