from ui.ui_font_dialog import Ui_FontDialog
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal

class FontDialog(QDialog, Ui_FontDialog):
    font_changed = pyqtSignal(QFont)
    
    def __init__(self):
        QDialog.__init__(self)
        Ui_FontDialog.__init__(self)
        self.setupUi(self)
        font = QApplication.instance().font()
        self.fontComboBox.setCurrentText(font.family())
        self.fontSizeSpinBox.setValue(font.pointSize())
        self.fontComboBox.currentTextChanged.connect(self.font_family_changed)
        self.fontSizeSpinBox.valueChanged.connect(self.font_size_changed)
        self._previous = (self.fontComboBox.currentText(), self.fontSizeSpinBox.value(), self.showChangeCheck.isChecked())
        
    def reset_to_previous(self):
        self.fontComboBox.setCurrentText(self._previous[0])
        self.fontSizeSpinBox.setValue(self._previous[1])
        self.showChangeCheck.setChecked(self._previous[2])
        
    def set_font(self, font:QFont):
        self.fontComboBox.setCurrentText(font.family())
        self.fontSizeSpinBox.setValue(font.pointSize())
        
    def font_family_changed(self, family:str):
        if self.showChangeCheck.isChecked():
            self.font_changed.emit(QFont(family, self.fontSizeSpinBox.value()))        
            
    def font_size_changed(self, size:int):
        if self.showChangeCheck.isChecked():
            self.font_changed.emit(QFont(self.fontComboBox.currentText(), size))    
            
    def exec_(self):
        result = super().exec_()
        if result == self.Accepted:
            self.font_changed.emit(QFont(self.fontComboBox.currentText(), self.fontSizeSpinBox.value()))
        else:
            self.reset_to_previous()
        return result