from PyQt5.QtWidgets import QWidget
from ui.ui_edit_text_widget import Ui_EditTextWidget

class _EditTextWidget(QWidget, Ui_EditTextWidget):
    def __init__(self, type):
        QWidget.__init__(self)
        Ui_EditTextWidget.__init__(self)
        self.setupUi(self)
        self.autoIndexBox.toggled.connect(self.auto_index_toggled)
        self.setIndexButton.clicked.connect(self.set_index_from_selected_text)
        self.textEdit.textChanged.connect(self.text_edit_changed)
        self._type = type
        self._autoIndex = None
        
    @property
    def type(self):
        return self._type
        
    def auto_index_toggled(self, auto:bool):
        self.setIndexButton.setEnabled(auto)
        self.incrementRadioButton.setEnabled(auto)
        self.decrementRadioButton.setEnabled(auto)
        self.indexLabel.setEnabled(auto)
        
    def set_index_from_selected_text(self):
        cursor = self.textEdit.textCursor()
        selectedText = cursor.selectedText()
        if selectedText:
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            self.indexLabel.setText(':   ' + selectedText)
            self._autoIndex = (start, end)
        else:
            text = self.textEdit.toPlainText()
            if text:
                text = text.strip()
                if text:
                    self.indexLabel.setText(':   ' + text)
                    self._autoIndex = (0, len(text))

    @property
    def auto_index_start(self):
        return self._autoIndex[0]
   
    @property
    def auto_index_end(self):
        return self._autoIndex[1]
    
    @property
    def has_auto_index(self):
        return self._autoIndex is not None
    
    @property
    def in_auto_index_mode_and_ready(self):
        return self.autoIndexBox.isChecked() and self._autoIndex is not None
    
    def set_auto_index(self, start:int, end:int):
        self._autoIndex = (start, end)
        
    def text_edit_changed(self):
        if self._autoIndex:
            start, end = self._autoIndex
            index = self.textEdit.toPlainText()[start:end]
            self.indexLabel.setText(':   ' + index)