from PyQt5.QtWidgets import QGraphicsScene, QUndoStack, QApplication, QMenu, QGraphicsItem
from PyQt5.QtGui import QColor, QPainter, QPen, QTransform, QDrag
from PyQt5.QtCore import QPointF, Qt, QMimeData, pyqtSignal #QElapsedTimer
from functools import cmp_to_key
from gfx.text import Text
from gfx.object import Object
from gfx.collision_responsive import CollisionResponsive
import _pickle as pickle
from gfx.arrow import Arrow
from gfx.linkable import Linkable
from core.qt_tools import (SimpleBrush, Pen, filter_out_descendents, first_ancestor_of_type, \
                      simple_max_contrasting_color)
from gfx.container import Container
from gfx.connectable import Connectable
from gfx.control_point import ControlPoint
from dialog.canvas_grid_dialog import CanvasGridDialog
from gfx.graphics_shape import GraphicsShape
from gfx.deletable import Deletable
from dialog.color_dialog import ColorDialog
from bidict import bidict
import re

class LanguageCanvas(QGraphicsScene):
    user_text_edited = pyqtSignal(Text)
    mouse_pressed = pyqtSignal(QPointF)
    set_definition_requested = pyqtSignal(QGraphicsItem)
    
    init_object_text = '{@A}'
    init_arrow_text = '{@a}'
    init_remark_text = "Remark"
    init_label_text = "Label"
    default_background_color = QColor(237, 255, 241)
    #double_click_timeout_ms = 200
    
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
        #self._doubleClickTimer = None
        self._variableIndices = bidict()
        self._arrowText = self.init_arrow_text
        self._objectText = self.init_object_text
        self._labelText = self.init_label_text

    def __setstate__(self, data:dict):
        self.__init__()
        self.setBackgroundBrush(data['background brush'])
        self._gridOrigin = data['grid origin']
        self.grid_dialog._setState(data['grid dialog'])
        self.background_color_dialog._setState(data['color dialog'])
        for item in data['items']:
            self.addItem(item)
        self._variableIndices = data['var indices']
        self._arrowText = data['arrow text']
        self._objectText = data['object text']
        self._labelText = data['label text']
    
    def __getstate__(self):
        items = list(filter_out_descendents(self.items()))
        return {
            'background brush' : self._backgroundBrush,
            'grid origin' : self._gridOrigin,
            'grid dialog' : self.grid_dialog._getState({}),
            'items' : items,
            'color dialog' : self.background_color_dialog._getState({}),
            'var indices' : self.variable_indices,
            'arrow text' : self._arrowText,
            'object text' : self._objectText,
            'label text' : self._labelText
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
        window = QApplication.activeWindow()
        item = self.itemAt(event.scenePos(), QTransform())
        
        if window.language_edit_mode == window.DefinitionMode:
            if isinstance(item, Linkable):
                if item.link is None:
                    item.user_navigates_to_link()
                else:
                    item.goto_link()
            event.accept()
                
        elif window.language_edit_mode == window.TextMode:            
            if not isinstance(item, Text):
                T = Text(html=self.label_text)
                T.set_contained_in_bbox(contained=False)
                self._addText(T, parent=item)
                if item is None:
                    T.setPos(event.scenePos())
                else:
                    T.setPos(item.mapFromScene(event.scenePos()))
                T.update()    
            else:
                super().mouseDoubleClickEvent(event)
            
        elif window.language_edit_mode == window.DefinitionMode:
            if item is not None:
                self.set_definition_requested.emit(item)
            else:
                X = Object(self.object_text)    
                self._addObject(X) 
                X.setPos(event.scenePos(), snap=True)
                X.update() 
                
        elif window.language_edit_mode == window.ArrowMode:
            if isinstance(item, ControlPoint):
                X = Object(self.object_text)
                parent = item.parentItem()
                self._addObject(X, parent.parentItem())                
                parent.set_at_point(item, X)    
                parent = parent.parentItem()
                if not parent:
                    X.setPos(event.scenePos(), snap=True)
                else:
                    X.setPos(parent.mapFromScene(event.scenePos()), snap=True)
                self.end_placing_control_point()
                X.update()
            else:                
                f = Arrow(text=self.arrow_text)
                if item is None:                
                    X = Object(self.object_text)    
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
        
    def _addText(self, T:Text, parent=None):
        from core.undo_cmd import AddText
        if parent:
            T.set_contained_in_bbox(False)
        self._undoStack.push(AddText(T, canvas=self, parent=parent))
            
    def undo_command(self):
        self._undoStack.undo()
        
    def redo_command(self):
        self._undoStack.redo()
        
    def mouseMoveEvent(self, event):
        from dialog.mainwindow import MainWindow
        window = QApplication.activeWindow()
        
        if isinstance(window, MainWindow):
            delta = event.scenePos() - event.lastScenePos()
            
            if self._controlPoint:
                self._controlPoint.setPos(self._controlPoint.pos() + delta)
            elif self._movedItems:
                for item in self._movedItems.values():
                    item.setPos(item.pos() + delta)
                    #if not isinstance(item, Text):
                        #for arrow in item.connectors:
                            #if id(arrow) not in self._movedItems:
                                #arrow.update()
            else:
                if window.language_edit_mode == window.MoveMode:
                    super().mouseMoveEvent(event)
        
    def mousePressEvent(self, event):
        self.mouse_pressed.emit(event.scenePos())        
        item = self.itemAt(event.scenePos(), QTransform())      
        superCall = True
        window = QApplication.activeWindow()
        
        if window.language_edit_mode in (window.MoveMode, window.ArrowMode, window.TextMode):
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
                                            parent = item.parentItem()
                                            
                                            if isinstance(parent, Object) and item.contained_in_bbox:
                                                self._movedItems[id(parent)] = parent
                                            
                                            elif item.flags() & item.ItemIsMovable:
                                                self._movedItems[id(item)] = item   
                                        
                                    self._movedItems = {id(item) : item for item in filter_out_descendents(self._movedItems.values()) }       
                                else:
                                    if isinstance(item, Text):
                                        parent = item.parentItem()
                                        if isinstance(parent, Object) and item.contained_in_bbox:
                                            item = parent
                                    self._movedItems = {id(item) : item}                            
                            if len(self._movedItems) == 1 and isinstance(list(self._movedItems.values())[0], Arrow):
                                self._movedItems.clear()
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
            
        #self._doubleClickTimer = None        
        
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
            #QApplication.instance().topmost_main_window.set_collision_response_enabled(self._collisionResponseSave)
        elif self._movedItems:
            from core.undo_cmd import MoveItems
            move_items = list(self._movedItems.values())
            self._movedItems.clear()    # BUGFIX: clearing moved items must come before updating, or the arrows won't update properly sometimes after snapping
            for item in move_items:
                if isinstance(item, Object):   # BUGFIX: remember to snap then update arrows here.
                    item.setPos(item.pos(), snap=True, update=True)           
            self._undoStack.push(MoveItems(self._movedItems.values(), event.scenePos() - self._startPos))
            self._startPos = None
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

        #QApplication.instance().topmost_main_window.stash_and_disable_collision_response()        
        
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
        from core.undo_cmd import DeleteItems
        self._undoStack.push(DeleteItems(items, canvas=self))
            
    def done_editing_text(self):
        if self._editText:
            from core.undo_cmd import EditText
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
        from core.undo_cmd import DropItems
        self._undoStack.push(DropItems(
            items, canvas=self, pos=event.scenePos(), move_action=False, parent=parent,
            source_items=mimeData.drag_items,
            source_canvas=mimeData.drag_from_canvas))
        #for item in items:
            #item.update()
            
        for item in items:
            if isinstance(item, Arrow):
                item.update()
                
        #QApplication.instance().topmost_main_window.restore_collision_response_setting()
                       
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
        window = QApplication.instance().topmost_main_window
        #self._collisionResponseSave = window.collision_response_enabled
        #window.set_collision_response_enabled(False)        
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
            w = 0.04 * (gridx + gridy) / 2
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
            #QApplication.instance().topmost_main_window().set_collision_response_enabled(self._collisionResponseSave)
            point.parentItem().update()
            
    @property
    def items_being_moved(self):
        return self._movedItems

    def parse_user_text(self, text:Text):
        self.user_text_edited.emit(text)
        
    @property
    def variable_indices(self):
        print(self._variableIndices)
        return self._variableIndices
    
    @property
    def object_text(self):
        text, self._objectText = self.auto_index_text(self._objectText)
        if not self._objectText:
            self._objectText = self.init_object_text            
        return text
    
    @property
    def arrow_text(self):
        text, self._arrowText = self.auto_index_text(self._arrowText)
        if not self._arrowText:
            self._arrowText = self.init_arrow_text
        return text
    
    @property
    def label_text(self):
        text, self._labelText = self.auto_index_text(self._labelText)
        if not self._labelText:
            self._labelText = self.init_label_text
        return text
    
    _autoIndexRegex = re.compile(r'{(?P<direc>-?)@(?P<index>.+)}')
    
    def auto_index_text(self, text:str) -> tuple:
        auto_index = text
        
        for match in self._autoIndexRegex.finditer(text):
            current_index = index = match.group('index')
            direc = match.group('direc')
            if direc == '-':
                direc = -1
            else:
                direc = 1
            try:
                index = int(index)
                index += direc
                index = str(index)
            except:
                index = ord(index[0])
                index += direc
                index = chr(index)
            if direc == -1:
                direc = "-@"
            else:
                direc = "@"
            next_index = f'{{{direc}{index}}}'
            auto_index = auto_index.replace(match.group(), next_index)
            text = text.replace(match.group(), current_index)
        return text, auto_index
    
    def text(self, text:str, item=None):
        parent = item.parentItem()
        text, auto_text = self.auto_index_text(text)
        if parent is None or (isinstance(item, Text) and not item.contained_in_bbox):
            self._labelText = auto_text
        elif isinstance(parent, Object):
            self._objectText = auto_text
        elif isinstance(parent, Arrow):
            self._arrowText = auto_text
        return text, auto_text
            