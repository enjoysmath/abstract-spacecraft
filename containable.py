from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QMenu

class Containable:
    def __init__(self):
        self._contained = True
        self._bbox = QRectF()

    def _setState(self, data):
        self._contained = data['contained']
        
    def _getState(self, data):
        data['contained'] = self._contained
        return data
            
    @property
    def contained_in_bbox(self):
        return self._contained
        
    def set_contained_in_bbox(self, contained:bool):
        if self._contained != contained:
            self._contained = contained
            self.update() 
            if contained == False:
                if self.scene():
                    self.scene().update()
                self.setFlag(self.ItemIsMovable, True)
            else:
                self.setFlag(self.ItemIsMovable, False)
                
    def boundingRect(self):
        return self._bbox
    
    def _updateBoundingRect(self):
        raise NotImplementedError
        
    def update(self):
        self.prepareGeometryChange()
        self._updateBoundingRect()
            
    def set_bounding_box(self, bbox:QRectF, update:bool=True):
        if self._bbox != bbox:
            self._bbox = bbox
            if update:
                self.update()
                
    def _itemChange(self, change, value):
        return value

    def build_context_menu(self, menu:QMenu, sep=False):
        if sep:
            menu.addSeparator()            
        if self.parentItem():
            if self._contained:
                menu.addAction("Free from parent's box").triggered.connect(lambda b: self.set_contained_in_bbox(False))
            else:
                menu.addAction("Bound by parent's box").triggered.connect(lambda b: self.set_contained_in_bbox(True))
            menu.addAction("Make adopted by grandparent").triggered.connect(lambda b: self.setParentItem(self.parentItem().parentItem()))
            menu.addAction("Orphan from parent into scene").triggered.connect(lambda b: self.setParentItem(None))
        return menu
                 
    def delete(self):
        for child in self.childItems():
            child.delete()
        self.setParentItem(None)
        if self.scene():
            self.scene().removeItem(self)  