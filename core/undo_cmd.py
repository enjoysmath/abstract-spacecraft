from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt, QPointF
from collections import OrderedDict
from graphics.object import Object
from graphics.language_canvas import LanguageCanvas
from graphics.arrow import Arrow
from core.geom_tools import center_scene_pos_of_items
from graphics.text import Text
from graphics.container import Container
from graphics.control_point import ControlPoint

class UndoCmd(QUndoCommand):
    pass

class AddObject(UndoCmd):
    def __init__(self, X:Object, canvas:LanguageCanvas=None, parent=None):
        super().__init__()
        self._ob = X
        self._canvas = canvas
        self._parent = parent
        
    def redo(self):
        if self._parent:
            self._ob.setParentItem(self._parent)
        else:
            self._canvas.addItem(self._ob)
        self._ob.bbox_collision_response()
                
    def undo(self):
        self._canvas.removeItem(self._ob)
        if self._parent:
            self._ob.setParentItem(None)
            
class AddArrow(UndoCmd):
    def __init__(self, f:Arrow, canvas:LanguageCanvas, parent=None):
        super().__init__()
        self._arr = f
        self._canvas = canvas
        self._parent = parent
        
    def redo(self):
        if self._parent:
            self._arr.setParentItem(self._parent)
        else:
            self._canvas.addItem(self._arr)
        #self._arr.bbox_collision_response()
                
    def undo(self):
        self._canvas.removeItem(self._arr)     
        if self._parent:
            self._arr.setParentItem(None)
            
class MoveItems(UndoCmd):
    def __init__(self, items:OrderedDict, delta_pos:QPointF):
        super().__init__()
        self._items = items
        self._skippedFirst = False
        self._deltaPos = delta_pos      
        
    def redo(self):
        if self._skippedFirst:
            for item in self._items:
                item.moveBy(self._deltaPos.x(), self._deltaPos.y())
                item.update()
        else:
            self._skippedFirst = True
            
    def undo(self):
        for item in self._items:
            item.moveBy(-self._deltaPos.x(), -self._deltaPos.y())
            item.update()
            
class DeleteItems(UndoCmd):
    def __init__(self, items:list, canvas:LanguageCanvas):
        super().__init__()
        self._items = []
        
        for item in items:
            if isinstance(item, ControlPoint):
                self._items.append(item.parentItem())
            else:
                self._items.append(item)
                
        self._canvas = canvas
        self._connectivity = {}
        
    def redo(self):
        for item in self._items:
            if isinstance(item, Arrow):
                self._connectivity[id(item)] = (item.parentItem(), item.source, item.destination)                
                item.set_source(None)
                item.set_destination(None)
            elif isinstance(item, (Object, Text)):
                self._connectivity[id(item)] = item.parentItem()
            item.setParentItem(None)
            self._canvas.removeItem(item)
            
    def undo(self):
        for item in self._items:
            if isinstance(item, Arrow):
                parent, source, dest = self._connectivity[id(item)]
                item.set_source(source)
                item.set_destination(dest)
            elif isinstance(item, (Object, Text)):
                parent = self._connectivity[id(item)]
            item.setParentItem(parent)
            self._canvas.addItem(item)
            
class EditText(UndoCmd):
    def __init__(self, item:Text, before:str):
        super().__init__()
        self._item = item
        self._before = before
        self._after = item.toHtml()
        self._skippedFirst = False
    
    def redo(self):
        if self._skippedFirst:
            self._item.setHtml(self._after)
        else:
            self._skippedFirst = True
            
    def undo(self):
        self._item.setHtml(self._before)
        
        
class DropItems(UndoCmd):
    def __init__(self, items:list, canvas:LanguageCanvas,  move_action:bool, pos:QPointF, parent:Container=None, 
                 source_items:list=None, source_canvas:LanguageCanvas=None):
        super().__init__()
        self._items = items
        self._canvas = canvas
        self._moveAction = move_action
        self._parent = parent
        self._sourceItems = source_items
        self._sourceCanvas = source_canvas
        self._centerPos = center_scene_pos_of_items(items)
        self._pos = pos
    
    def redo(self):
        posOffs = self._pos - self._centerPos        
        if self._parent:
            for item in self._items:
                item.setPos(self._parent.mapFromScene(posOffs + item.scenePos()))
                item.setParentItem(self._parent)
        else:
            for item in self._items:
                item.setPos(posOffs + item.scenePos())
                self._canvas.addItem(item)
                
        if self._moveAction and self._sourceItems and self._sourceCanvas:
            for item in self._sourceItems:
                self._sourceCanvas.removeItem(item)
                
    def undo(self):
        if self._parent:
            for item in self._items:
                item.setParentItem(None)
                self._canvas.removeItem(item)
        else:
            for item in self._items:
                self._canvas.removeItem(item)
        if self._moveAction and self._sourceItems and self._sourceCanvas:
            for item in self._sourceItems:
                self._sourceCanvas.addItem(item)