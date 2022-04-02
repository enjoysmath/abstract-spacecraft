from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Connectable:   
    def __init__(self):
        self._connectors = []
        
    def _setState(self, data:dict):
        self._connectors = data['connectors']
        
    def _getState(self, data:dict):
        data['connectors'] = self._connectors
        return data
    
    @property
    def connectors(self):
        return self._connectors
        
    def delete(self):
        for c in self._connectors:
            c._setConnectable(self, None)
        self.setParentItem(None)
        if self.scene():
            self.scene().removeItem(self)

    def _connect(self, c):
        self._connectors.append(c)
        
    def _disconnect(self, c):
        self._connectors.remove(c)
        
    def _itemChange(self, change, value):
        if change == self.ItemChildAddedChange:
            self.update()
        elif change == self.ItemChildRemovedChange:
            self.update()
        return value
    
    def boundingRect(self):
        return self._bbox
        
    def _updateBoundingBox(self):
        bbox = self.childrenBoundingRect()
        p = self._bboxPad
        self._bbox = bbox.adjusted(-p, -p, p, p)   
               
    def delete_associated_if_not_in(self, item_set:set):
        for connector in self._connectors:
            if id(connector) not in item_set:
                self._disconnect(connector)
            connector.delete_associated_if_not_in(item_set)            
        if id(self) not in item_set:
            self.delete()
    
    @property
    def total_degree(self):
        return len(self._connectors)
    
    def update_connectors(self):
        for conn in self._connectors:
            conn.update()                

class Connector(Connectable):
    Source, Dest = range(2)
    
    def __init__(self, source=None, dest=None):
        super().__init__()
        self._connected = [None, None]
        self.set_source(source)
        self.set_destination(dest)
        
    def _setState(self, data:dict):
        Connectable._setState(self, data['connectable'])
        self._connected = data['connected']
                
    def _getState(self, data:dict):
        data['connected'] = self._connected
        data['connectable'] = Connectable._getState(self, {})
        return data
               
    def _setAt(self, i:int, c:Connectable):
        conn = self._connected
        if conn[i] is not c:
            if conn[i] is not None:
                #self._disconnect(conn[i])
                conn[i]._disconnect(self)
            conn[i] = c
            if c is not None:
                #self._connect(c)
                c._connect(self)
            self.update()
        
    def _setConnectable(self, c:Connectable, d:Connectable):
        conn = self._connected
        for i in range(len(conn)):
            if conn[i] is c:
                conn[i] = d
                
    @property
    def source(self):
        return self._connected[self.Source]
    
    @property
    def destination(self):
        return self._connected[self.Dest]
    
    def set_source(self, source:Connectable):
        self._setAt(self.Source, source)
        
    def set_destination(self, dest:Connectable):
        self._setAt(self.Dest, dest)
        
    def delete_associated_if_not_in(self, item_set:dict):
        if self.source and id(self.source) not in item_set:
            self.source.delete_associated_if_not_in(item_set)
            self.source.delete()
            self.set_source(None)
        if self.destination and id(self.destination) not in item_set:
            self.destination.delete_associated_if_not_in(item_set)
            self.destination.delete()
            self.set_destination(None)
        if id(self) not in item_set:
            self.delete()
        

            
    
