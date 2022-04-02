from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit

class LineEdit(QLineEdit):
    editing_started = pyqtSignal()
    
    def __init__(self, parent=None): 
        super().__init__(parent)
    
        self._editMode = False
        self.editingFinished.connect(lambda: self.set_edit_mode(False))

    def set_edit_mode(self, en):
        if en != self._editMode:
            self._editMode = en

    def mousePressEvent(self, event):
        if not self._editMode: # i forgot that... i prefer !
            self.set_edit_mode(True)
            self.editing_started.emit()
            
        super().mousePressEvent(event)
     
        
        
    
    