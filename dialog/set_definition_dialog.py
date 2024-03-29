from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow
from ui.ui_set_definition_dialog import Ui_SetDefinitionDialog
from PyQt5.QtCore import Qt
from gfx.linkable import Linkable

class SetDefinitionDialog(QDialog, Ui_SetDefinitionDialog):  
    def __init__(self):
        QDialog.__init__(self)
        Ui_SetDefinitionDialog.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.externalLinkRadio.toggled.connect(self.externalUrlLine.setEnabled)
        self.externalLinkRadio.toggled.connect(self.externalLinkTextLine.setEnabled)
        self.accepted.connect(self.ok_clicked)
        self.bypassDialogCheck.toggled.connect(self.bypassDialogTimesSpin.setEnabled)
        self._bypassCount = None
        
    def ok_clicked(self):
        if self.externalLinkRadio.isChecked():
            app = QApplication.instance()
            app.link_requester.set_link((self.externalUrlLine.text(), self.externalLinkTextLine.text()))
            app.set_link_requester(None)
            
        if self.bypassDialogCheck.isChecked():
            self._bypassCount = 0
        
            
    def show(self):
        if self._bypassCount is not None and self._bypassCount < self.bypassDialogTimesSpin.value():
            self._bypassCount += 1
            return
        else:
            self._bypassCount = None
        super().show()