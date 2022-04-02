from PyQt5.QtWidgets import (QDockWidget, QGridLayout, QApplication, QPlainTextEdit, QPushButton,
                             QWidget)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from ui_edit_text_dockwidget import Ui_EditTextDockWidget
from edit_text_widget import EditTextWidget
from object import Object
from arrow import Arrow
from text import Text
from unicode_tools import check_for_int
from unicode_support import UnicodeSupport
from bidict import bidict

class EditTextDockWidget(QDockWidget, Ui_EditTextDockWidget):
    def __init__(self):
        QDockWidget.__init__(self)
        Ui_EditTextDockWidget.__init__(self)
        self.setupUi(self)
        self.arrowTab.setLayout(QGridLayout())
        self.objectTab.setLayout(QGridLayout())
        self._objectWidget = EditTextWidget(type=Object)
        self._arrowWidget = EditTextWidget(type=Arrow)
        self.arrowTab.layout().addWidget(self._arrowWidget)
        self.objectTab.layout().addWidget(self._objectWidget)
        self.setSelectedButton.clicked.connect(self.set_selected_text_items)
        self.unicodeShapeCatcherButton.clicked.connect(
            lambda x: QDesktopServices.openUrl(QUrl('https://shapecatcher.com/')))
        self._unicodeSupport = UnicodeSupport()
        
    @property
    def unicode_support(self):
        return self._unicodeSupport
                
    def set_selected_text_items(self):
        type = None
        text = None        
        widget = self.current_item_type_widget()
        type = widget.type
        text = widget.textEdit.toPlainText()   
        
        if type:
            window = QApplication.activeWindow()
            view = window.current_language_view
            if view:
                scene = view.scene()
                if scene:
                    items = scene.selectedItems()
                    items = filter(lambda x: isinstance(x.parentItem(), type) and isinstance(x, Text), items )
                    
                    if not self.current_item_type_widget().in_auto_index_mode_and_ready:                        
                        for item in items:
                            item.setHtml(text)
                    else:
                        # Auto-indexing should be performed on the naturally ordered list of selected items:
                        items = sorted(items, key=lambda x: [x.scenePos().y(), x.scenePos().x()])
                        for item in items:
                            item.setHtml(self.next_auto_indexed_text(widget))
                        
    def current_auto_index_groupbox(self):
        current = self.itemTypeTabs.currentWidget()
        if current is self.objectTab:
            return self._objectWidget.autoIndexBox
        elif current is self.arrowTab:
            return self._arrowWidget.autoIndexBox
        raise NotImplementedError
                                
    def _nextAutoIndex(self, widget:EditTextWidget, inc=True):      
        text = widget.textEdit.toPlainText()            
        start = widget.auto_index_start
        end = widget.auto_index_end
        index = text[start:end]
        prefix = text[:start]
        integer, charmap = check_for_int(index)
        if integer is not None:
            if inc:
                integer += 1
            else:
                integer -= 1
            index = charmap(integer)
            suffix = text[end:]
            widget.set_auto_index(start, start+len(index))
        else:
            index = self._nextLetterIndex(index[0], inc)
            suffix = text[end - len(index) + 1:]
        text = prefix + index + suffix
        widget.textEdit.setPlainText(text)   
        widget.indexLabel.setText(':   ' + index)

    character_special_sets = (
        bidict({ c : chr(ord('a') + ((c + 1) % 26)) for c in range(ord('a'), ord('z') + 1)}),
        bidict({ C : chr(ord('A') + ((C + 1) % 26)) for C in range(ord('A'), ord('Z') + 1)}),
        bidict({ 
            'α' : 'β',
            'β' : 'γ',   
            'γ' : 'δ',
            'δ' : 'ε',   
            'ε' : 'ζ',
            'ζ' : 'η',   
            'η' : 'θ',
            'θ' : 'ι',   
            'ι' : 'κ',
            'κ' : 'λ',   
            'λ' : 'μ',
            'μ' : 'ν',   
            'ν' : 'ξ',
            'ξ' : 'ο',   
            'ο' : 'π',
            'π' : 'ρ',   
            'ρ' : 'ς',
            'ς' : 'σ',   
            'σ' : 'τ',
            'τ' : 'υ',   
            'υ' : 'φ',
            'φ' : 'χ',   
            'χ' : 'ψ',
            'ψ' : 'ω',   
            'ω' : 'α',
        }))
        
    def _nextLetterIndex(self, c:chr, inc:bool=True):
        for special in self.character_special_sets:
            if c in special:
                if inc:
                    return special[c]
                else:
                    return special.inv[c]
                    
        try:
            start, end = self.unicode_support.contiguous_range(c)
        except:
            start = ord(c) - 1
            end = ord(c) + 1
        
        try:                
            if inc:
                if ord(c) + 1 == start + end:
                    return chr(start)
                return chr(ord(c) + 1)
            else:
                if ord(c) == start:
                    return chr(end - 1)
                return chr(ord(c) - 1)
        except:
            return '�'
        
    def increment_auto_index(self, widget:EditTextWidget):
        self._nextAutoIndex(widget)
        
    def decrement_auto_index(self, widget:EditTextWidget):
        self._nextAutoIndex(widget, inc=False)
        
    def next_auto_indexed_text(self, widget:EditTextWidget=None):
        if widget is None:
            widget = self.current_item_type_widget()
        text = widget.textEdit.toPlainText()
        if widget.incrementRadioButton.isChecked():
            self.increment_auto_index(widget)
        elif widget.decrementRadioButton.isChecked():
            self.decrement_auto_index(widget)
        else:
            raise NotImplementedError
        return text
    
    def current_item_type_widget(self):
        if self.itemTypeTabs.currentWidget() is self.objectTab:
            return self._objectWidget
        elif self.itemTypeTabs.currentWidget() is self.arrowTab:
            return self._arrowWidget
        raise NotImplementedError
    
    
    