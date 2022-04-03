from PyQt5.QtWidgets import QGraphicsScene, QUndoStack, QApplication, QMenu
from PyQt5.QtGui import QColor, QPainter, QPen, QTransform, QDrag
from PyQt5.QtCore import QPointF, Qt, QMimeData, pyqtSignal
from functools import cmp_to_key
from graphics.text import Text
from graphics.object import Object
from graphics.collision_responsive import CollisionResponsive
import _pickle as pickle
from graphics.arrow import Arrow
from core.qt_tools import (SimpleBrush, Pen, filter_out_descendents, first_ancestor_of_type, \
                      simple_max_contrasting_color)
from graphics.container import Container
from graphics.connectable import Connectable
from graphics.control_point import ControlPoint
from dialog.canvas_grid_dialog import CanvasGridDialog
from graphics.graphics_shape import GraphicsShape
from graphics.deletable import Deletable
from dialog.color_dialog import ColorDialog

class LanguageCanvas(QGraphicsScene):
    mouse_pressed = pyqtSignal(QPointF)
    init_object_text = '🌍'
    init_arrow_text = '🚀'
    default_background_color = QColor(237, 255, 241)
    
    def __init__(self):
        super().__init__()
        self._backgroundBrush = None
        self.setBackgroundBrush(SimpleBrush(self.default_background_color))
        self._undoStack = QUndoStack()
        self._startPos = None
        self._movedItems = {}
        self._editText = None
        self._textBeforeEdit = None
        self._controlPoint = None
        self._controlPointSkip1Release = False
        self._gridOrigin = QPointF(0,0)
        self.grid_dialog = CanvasGridDialog()
        self.grid_dialog.redraw_canvas_background.connect(self.update)
        self.background_color_dialog = ColorDialog(title='Background color')
        self.background_color_dialog.currentColorChanged.connect(lambda col: self.setBackgroundBrush(SimpleBrush(col)))
        self.background_color_dialog.setCurrentColor(self.backgroundBrush().color())
                
    def __setstate__(self, data:dict):
        self.__init__()
        self.setBackgroundBrush(data['background brush'])
        self._gridOrigin = data['grid origin']
        self.grid_dialog._setState(data['grid dialog'])
        self.background_color_dialog._setState(data['color dialog'])
        for item in data['items']:
            self.addItem(item)
    
    def __getstate__(self):
        items = list(filter_out_descendents(self.items()))
        return {
            'background brush' : self._backgroundBrush,
            'grid origin' : self._gridOrigin,
            'grid dialog' : self.grid_dialog._getState({}),
            'items' : items,
            'color dialog' : self.background_color_dialog._getState({}),
        }
    
    def addItem(self, item:GraphicsShape):
        if isinstance(item, Deletable):
            item.delete_requested.connect(lambda: self.delete_items([item]))
        super().addItem(item)
        item.update()
    
    def setBackgroundBrush(self, brush:SimpleBrush):
        if brush != self._backgroundBrush:
            self._backgroundBrush = brush
            super().setBackgroundBrush(brush)
            self.update()
            
    def backgroundBrush(self):
        return self._backgroundBrush

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        window = QApplication.activeWindow()
        if not window.place_arrow_mode:
            if item is None:            
                # Canvas background clicked
                X = Object(self.init_object_text)    
                self._addObject(X) 
                X.setPos(event.scenePos(), snap=True)
                X.update()
            else:
                if isinstance(item, Text) and window.edit_text_mode:
                    super().mouseDoubleClickEvent(event)
                    return                                
                item = first_ancestor_of_type(Container, item)   
                if item:
                    X = Object(self.init_object_text)
                    self._addObject(X, parent=item)
                    X.setPos(X.mapFromScene(event.scenePos()), snap=True)
        else:
            if isinstance(item, ControlPoint):
                X = Object(self.init_object_text)
                parent = item.parentItem()
                self._addObject(X, parent.parentItem())                
                parent.set_at_point(item, X)    
                parent = parent.parentItem()
                if not parent:
                    X.setPos(event.scenePos())
                else:
                    X.setPos(parent.mapFromScene(event.scenePos()), snap=True)
                self.end_placing_control_point()
                X.update()
            else:                
                f = Arrow(text=self.init_arrow_text)
                if item is None:                
                    #self._addArrow(f)
                    #f.destination_point.setPos(f.mapFromScene(event.scenePos() + QPointF(50, 0)))
                    #f.update()
                    # Canvas background clicked
                    X = Object(self.init_object_text)    
                    self._addObject(X) 
                    X.setPos(event.scenePos(), snap=True)
                    X.update()                    
                else:
                    if isinstance(item, Text) and window.edit_text_mode:
                        super().mouseDoubleClickEvent(event)
                        return                
                    item = first_ancestor_of_type(Connectable, item)
                    if item:
                        f.set_source(item)
                    self._addArrow(f, parent=item.parentItem())
                    f.destination_point.setPos(f.mapFromScene(event.scenePos())) 
                    self.place_control_point(f.destination_point, skip_release=True)                
                f.source_point.setPos(f.mapFromScene(event.scenePos()))
                f.update() 
                        
    def _addObject(self, X:Object, parent=None):
        from core.undo_cmd import AddObject
        self._undoStack.push(AddObject(X, canvas=self, parent=parent))
        
    def _addArrow(self, f:Arrow, parent=None):
        from core.undo_cmd import AddArrow
        self._undoStack.push(AddArrow(f, canvas=self, parent=parent))
            
    def undo_command(self):
        self._undoStack.undo()
        
    def redo_command(self):
        self._undoStack.redo()
        
    def mouseMoveEvent(self, event):
        delta = event.scenePos() - event.lastScenePos()
        if self._controlPoint:
            self._controlPoint.setPos(self._controlPoint.pos() + delta)
        elif self._movedItems:
            for item in self._movedItems.values():
                item.setPos(item.pos() + delta)
                if not isinstance(item, Text):
                    for arrow in item.connectors:
                        if id(arrow) not in self._movedItems:
                            arrow.update()
        else:
            super().mouseMoveEvent(event)
        
    def mousePressEvent(self, event):
        self.mouse_pressed.emit(event.scenePos())        
        item = self.itemAt(event.scenePos(), QTransform())      
        superCall = True
        
        if event.button() == Qt.LeftButton: 
            if item:
                if item is not self._editText:   
                    if self._controlPoint is None:
                        if isinstance(item, ControlPoint):
                            self.place_control_point(item, skip_release=False)   
                            superCall = False   # BUGFIX
                            event.accept()      # BUGFIX
                            # These last two lines fix a bug, where the control point
                            # would jump away from the cursor and sometimes into hyperspace.                            
                        elif QApplication.keyboardModifiers() & Qt.ControlModifier:
                            if not isinstance(item, Text):
                                item.setSelected(not item.isSelected())
                        else:
                            self._startPos = event.scenePos()
                            if item.isSelected():
                                itemsToMove = self.selectedItems() 
                                itemsToMove = {id(item): item for item in itemsToMove}
                                                                
                                for item in itemsToMove.values():          
                                    if isinstance(item, (Arrow, Object)):
                                        self._movedItems[id(item)] = item   
                                        for arrow in item.connectors:
                                            if id(arrow) not in itemsToMove and id(arrow) not in self._movedItems:
                                                if id(arrow.source) in itemsToMove and id(arrow.destination) in itemsToMove:
                                                    self._movedItems[id(arrow)] = arrow
                                    elif isinstance(item, Text):
                                        if item.flags() & item.ItemIsMovable:
                                            self._movedItems[id(item)] = item
                                                    
                                self._movedItems = {id(item) : item for item in filter_out_descendents(self._movedItems.values()) }
                                                                                         
                            else:
                                self._movedItems = {id(item) : item}
                    else:
                        self.connect_arrow_by_control_point(self.items(event.scenePos()))
        elif event.button() == Qt.RightButton and \
             QApplication.keyboardModifiers() & Qt.ControlModifier:
            if self._controlPoint:
                self.end_placing_control_point()
            else:
                if item:
                    if item is not self._editText:
                        self.start_drag_items(item, event)
                
        if self._editText and self._editText is not item:
            self.done_editing_text()
            
        if superCall:
            super().mousePressEvent(event)
        
    #TODO: deleting an item must update each UndoCmd with items
    
    def mouseReleaseEvent(self, event):
        if self._controlPointSkip1Release:
            self._controlPointSkip1Release = False
        elif self._controlPoint:
            item = self.itemAt(event.scenePos(), QTransform())
            if item:
                self.connect_arrow_by_control_point(self.items(event.scenePos()))
            else:
                self.end_placing_control_point()
            QApplication.instance().topmost_main_window().set_collision_response_enabled(self._collisionResponseSave)
        elif self._movedItems:
            from core.undo_cmd import MoveItems
            for item in self._movedItems.values():
                item.update()
            self._undoStack.push(MoveItems(self._movedItems.values(), event.scenePos() - self._startPos))
            self._startPos = None
            self._movedItems = {}
        super().mouseReleaseEvent(event)
        
    def start_drag_items(self, item, event):        
        if item.isSelected():
            dragItems = self.selectedItems()
            dragItems = list(filter_out_descendents(dragItems))            
            dragItems = [x.use_another_drag_item() for x in dragItems]
        else:
            if isinstance(item, (Arrow, Object, Text)):
                dragItems = [item.use_another_drag_item()]
            else:
                return
                
        mimeData = QMimeData()
        mimeData.drag_items = dragItems
        mimeData.drag_from_canvas = self
        data = self.pickle_items(dragItems)
        mimeData.setData('application/octet-stream', data)
        
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.screenPos())

        QApplication.instance().topmost_main_window().stash_and_disable_collision_response()        
        
        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            mimeData.drag_action = Qt.CopyAction
            drag.exec_(Qt.CopyAction)                        
        else:
            mimeData.drag_action = Qt.MoveAction
            drag.exec_(Qt.MoveAction)   
        
    def set_edit_text(self, text:Text):
        if self._editText != text:
            if self._editText:
                self.done_editing_text()
            self._textBeforeEdit = text.toHtml()
            self._editText = text
            
    def delete_selected(self):
        items = self.selectedItems()
        if items:
            self.delete_items(items)
            
    def delete_items(self, items):
        from undo_cmd import DeleteItems
        self._undoStack.push(DeleteItems(items, canvas=self))
            
    def done_editing_text(self):
        if self._editText:
            from undo_cmd import EditText
            self._editText.done_editing()
            self._undoStack.push(EditText(self._editText, before=self._textBeforeEdit))
            self._editText = None        
            self._textBeforeEdit = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/octet-stream'):
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        mimeData = event.mimeData()
        items = self.unpickle_items(mimeData.data('application/octet-stream'))
        parent = self.itemAt(event.scenePos(), QTransform())
        if not isinstance(parent, Container):
            parent = None
        from undo_cmd import DropItems
        self._undoStack.push(DropItems(
            items, canvas=self, pos=event.scenePos(), move_action=False, parent=parent,
            source_items=mimeData.drag_items,
            source_canvas=mimeData.drag_from_canvas))
        #for item in items:
            #item.update()
            
        for item in items:
            if isinstance(item, Arrow):
                item.update()
                
        QApplication.instance().topmost_main_window().restore_collision_response_setting()
                       
    @staticmethod
    def pickle_items(items:list):
        items = LanguageCanvas.copy_items(items)
        items = pickle.dumps(items)
        return items
        
    @staticmethod
    def copy_items(items:list):
        data = pickle.dumps(items)    
        data = pickle.loads(data)
        return data
        
    @staticmethod
    def unpickle_items(data):
        items = pickle.loads(data)
        return items
            
    def place_control_point(self, ctrl_point, skip_release=False):
        window = QApplication.instance().topmost_main_window()
        self._collisionResponseSave = window.collision_response_enabled
        window.set_collision_response_enabled(False)        
        if ctrl_point.parentItem():
            ctrl_point.parentItem().set_at_point(ctrl_point, None)
            self._controlPoint = ctrl_point
            self._controlPointSkip1Release = skip_release
            return True
        return False
        
    def connect_arrow_by_control_point(self, items):
        parent = self._controlPoint.parentItem()
        for item in items:
            if item is not parent and isinstance(item, Connectable):
                self._controlPoint.parentItem().set_at_point(self._controlPoint, item) 
                break
        self.end_placing_control_point()
        item.update()
        
    def grid_sizex(self):
        return self.grid_dialog.xSpacingSpin.value()
    
    def grid_sizey(self):
        return self.grid_dialog.ySpacingSpin.value()
    
    def snap_grid_enabled(self):
        return self.grid_dialog.enabledCheck.isChecked()
    
    def snap_grid_visible(self):
        return self.grid_dialog.visibleCheck.isChecked()
    
    def grid_origin(self):
        return self._gridOrigin
       
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if self.snap_grid_enabled() and self.snap_grid_visible():
            painter.setRenderHints(QPainter.Antialiasing)
            gridx = int(self.grid_sizex() + 0.5)
            gridy = int(self.grid_sizey() + 0.5)
            w = 0.02 * (gridx + gridy) / 2
            painter.setPen(QPen(simple_max_contrasting_color(self.backgroundBrush().color()), w))
            points = []                 # Adding to a list and then drawing is much faster
            o = self.grid_origin()
            ox = o.x() % gridx
            oy = o.y() % gridy
            left = int(rect.left()) - (int(rect.left()) % gridx)
            top = int(rect.top()) - (int(rect.top()) % gridy)
            for x in range(left, int(rect.right()), gridx):
                for y in range(top, int(rect.bottom()), gridy):
                    points.append(QPointF(x + ox, y + oy))
            if points:
                painter.drawPoints(*points)
            # Draw grid origin
            #painter.drawLine(QLineF(o.x(), o.y() - 20, o.x(), o.y() + 20))
            #painter.drawLine(QLineF(o.x() - 20, o.y(), o.x() + 20, o.y()))          
            
    def build_context_menu(self, screen_pos):
        menu = QMenu()
        menu.addAction('Snap grid...').triggered.connect(lambda b: self.show_snap_grid_dialog(screen_pos))
        menu.addAction('Background color...').triggered.connect(lambda b: self.background_color_dialog.exec_())
        return menu    
    
    def show_snap_grid_dialog(self, screen_pos):
        result = self.grid_dialog.exec_()
        if result == self.grid_dialog.Accepted:
            return
        self.grid_dialog.reset_to_previous()
                
    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if not item:
            menu = self.build_context_menu(event.screenPos())        
            menu.exec_(event.screenPos())
        else:
            super().contextMenuEvent(event)
            
    @property
    def is_moving_items(self):
        return self._movedItems or self._controlPoint is not None
            
    def end_placing_control_point(self):
        if self._controlPoint:                
            point = self._controlPoint
            self._controlPoint = None
            self._controlPointSkip1Release = False
            QApplication.instance().topmost_main_window().set_collision_response_enabled(self._collisionResponseSave)
            point.parentItem().update()
            
    @property
    def items_being_moved(self):
        return self._movedItems