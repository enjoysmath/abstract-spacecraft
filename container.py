from containable import Containable
from PyQt5.QtCore import QRectF

class Container:
    def __init__(self):
        self.setFiltersChildEvents(True)
        
    def _setState(self, data:dict):
        for child in data['children']:
            child.setParentItem(self)
    
    def _getState(self, data:dict):
        data['children'] = self.childItems()
        return data
    
    def _sceneEventFilter(self, watched, event):
        if event.type() in (event.GraphicsSceneMouseMove, event.GraphicsSceneDragMove):
            self.update()
    
    def itemChange(self, change, value):
        if change == self.ItemChildAddedChange:
            value.installSceneEventFilter(self)
            value.setFlag(self.ItemSendsGeometryChanges, True)
        elif change == self.ItemChildRemovedChange:
            value.removeSceneEventFilter(self)
            self.delete_ancestory_chain_if_no_children()
        return value
    
    def count_children_of_type(self, type):
        count = 0
        for child in self.childItems():
            if isinstance(child, type):
                count += 1 
        return count
    
    def delete_ancestory_chain_if_no_children(self):
        if len(self.childItems()) == 0:
            parent = self.parentItem()
            self.delete()
            if parent:
                parent.delete_ancestory_chain_if_no_children()
            
    def delete(self):
        for child in self.childItems():
            child.delete()
        self.setParentItem(None)
        if self.scene():
            self.scene().removeItem(self)        

    @property
    def minimum_bbox(self):
        return QRectF(-5,-5,10,10)
    