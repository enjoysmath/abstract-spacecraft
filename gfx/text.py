from PyQt5.QtWidgets import QGraphicsTextItem, QMenu, QApplication
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtCore import Qt, QPointF, QRectF, QObject #QElapsedTimer
from gfx.containable import Containable
from gfx.collision_responsive import CollisionResponsive
from gfx.drag_droppable import DragDroppable
from gfx.definable import Definable
from gfx.snappable import Snappable
from core.qt_tools import unpickle_gfx_item_flags
from gfx.deletable import Deletable
from gfx.has_context_menu import HasContextMenu
import gfx.container

class Text(QGraphicsTextItem, Containable, CollisionResponsive, DragDroppable, Definable, 
           Snappable, HasContextMenu, Deletable):
    default_interaction = Qt.NoTextInteraction # Qt.TextBrowserInteraction  TODO have this be a context menu check option
    #_collisionSave = None     # Used for a bugfix
    
    def __init__(self, html:str=None):
        QGraphicsTextItem.__init__(self)
        Containable.__init__(self)
        CollisionResponsive.__init__(self)
        DragDroppable.__init__(self)
        Definable.__init__(self)
        Snappable.__init__(self)
        HasContextMenu.__init__(self)
        Deletable.__init__(self)
        self._html = None
        if html is not None:            
            self.setHtml(html)
        self.setFlags(self.ItemIsFocusable | self.ItemSendsGeometryChanges | self.ItemIsSelectable)
        self.setTextInteractionFlags(self.default_interaction)
        self.setOpenExternalLinks(True)
        self._bbox = super().boundingRect()
        self.set_snap_to_grid(False)
        self.setFont(QApplication.instance().font())
        self._center = self._bbox.center()
        self._restorePos = None
        #self._doubleClickTimer = None
        
    def __setstate__(self, data:dict):
        self.__init__(data['html'])
        self.setFlags(unpickle_gfx_item_flags(data['flags']))
        self.setDefaultTextColor(data['color'])
        self.setPos(data['pos'])
        Containable._setState(self, data['containable'])
        DragDroppable._setState(self, data['drag droppable'])
        Definable._setState(self, data['definable'])
        Deletable._setState(self, data['deletable'])
        
    def __getstate__(self):
        return {
            'html' : self._html,
            'flags' : int(self.flags()),
            'color' : self.defaultTextColor(),
            'pos' : self.pos(),
            'containable' : Containable._getState(self, {}),
            'drag droppable' : DragDroppable._getState(self, {}),
            'definable' : Definable._getState(self, {}),
            'deletable' : Deletable._getState(self, {}),
        }
                        
    def update(self):
        if QApplication.instance().topmost_main_window().text_collision_response_enabled:
            self.bbox_collision_response()
        Containable.update(self)
        super().update()
        #parent = self.parentItem()
        
        #from gfx.arrow import Arrow        
        #if parent:
            #if isinstance(parent, Arrow):
                #if parent.parentItem():
                    #parent.parentItem().update()
            #else:
                #self.parentItem().update()        
        
    def mouseDoubleClickEvent(self, event):
        if self.scene():       
            #window = QApplication.instance().topmost_main_window()
            #self._collisionSave = window.collision_enabled
            self.scene().set_edit_text(self)
            self.setPlainText(self._html)            
            cursor = self.textCursor()
            cursor.select(cursor.Document)
            self.setTextCursor(cursor)            
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.update()
            self.setFocus()            
                    
    def keyPressEvent(self, event):
        self.parse_user_text()
        super().keyPressEvent(event)
        
    def mousePressEvent(self, event):
        #if self._doubleClickTimer is None:
            #self._doubleClickTimer = QElapsedTimer()
            #self._doubleClickTimer.start()
            #return
        #elif not self._doubleClickTimer.hasExpired(self.scene().double_click_timeout_ms):
            #return
         
        from gfx.object import Object
        if self._restorePos is None and isinstance(self.parentItem(), Object):
            self._restorePos = self.pos()
        super().mousePressEvent(event)
            #self._doubleClickTimer = None
        
    def mouseReleaseEvent(self, event):
        from gfx.object import Object
        parent = self.parentItem()
        
        if isinstance(parent, Object):
            if self._restorePos is not None:
                self.setPos(self._restorePos)
                pos = event.scenePos()
                pos = parent.mapToParent(parent.mapFromScene(pos))
                parent.setPos(pos, snap=True)
                parent.update_connectors()
                self._restorePos = None
            
        super().mouseReleaseEvent(event)
        
    def _updateBoundingRect(self):
        self._bbox = super().boundingRect()    

    def done_editing(self):
        self.setTextInteractionFlags(self.default_interaction)
        self._html = None
        self.setHtml(self.toPlainText())
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        #QApplication.instance().topmost_main_window().set_collision_enabled(self._collisionSave)
        rect = self.boundingRect()
        delta = rect.center() - self._center
        parent = self.parentItem()
        from gfx.object import Object
        if isinstance(parent, Object):
            pos = parent.mapToParent(parent.mapFromScene(parent.scenePos() + delta))
            parent.setPos(pos, snap=True)
            parent.update_connectors()     
        else:
            self.setPos(self.pos() + delta)
        self._center = rect.center()

    def toHtml(self):
        return self._html
        
    def setHtml(self, html:str):
        if self._html != html:
            self._html = html
            super().setHtml(html)
            self.update()
            
    def itemChange(self, change, value):
        if QApplication.instance().topmost_main_window().text_collision_response_enabled:
            value = CollisionResponsive._itemChange(self, change, value)
        #if change == self.ItemPositionChange:
            #parent = self.parentItem()
            #if parent and parent.count_children_of_type(Text) == 1:
                #pos = self.pos()
                #parent.setPos(parent.pos() + self.mapToScene(value - pos))
                #value = pos
        if change == self.ItemPositionHasChanged:
            self.update()
        if change == self.ItemSelectedChange:
            #if self.parentItem() and self.parentItem().count_children_of_type(QObject) == 1:
                #self.parentItem().setSelected(value)
                #value = not value
            pass
        return super().itemChange(change, value)
    
    def dragEnterEvent(self, event):
        DragDroppable.dragEnterEvent(self, event)
    
    def dragLeaveEvent(self, event):
        DragDroppable.dragLeaveEvent(self, event)
    
    def dropEvent(self):
        DragDroppable.dropEvent(self, event)    
        
    def use_another_drag_item(self):
        if self.parentItem() is not None:
            if isinstance(self.parentItem(), gfx.container.Container) and self.parentItem().count_children_of_type(QObject) == 1:
                return self.parentItem()
        return self
    
    def build_context_menu(self, menu=None):
        parent = self.parentItem()
        if menu is None:
            menu = QMenu()
        oneNodeOneLabel = self.is_single_node_and_label()
        if oneNodeOneLabel:
            menu.addSection(self.__class__.__name__)
            
        Definable.build_context_menu(self, menu)
        Containable.build_context_menu(self, menu)
        Snappable.build_context_menu(self, menu)
        Deletable.build_context_menu(self, menu)        
        
        if oneNodeOneLabel:
            menu.addSection(parent.__class__.__name__)
            parent.build_context_menu(menu)
        return menu
    
    def is_single_node_and_label(self):
        parent = self.parentItem()
        siblings = parent.childItems()
        if parent and isinstance(parent, HasContextMenu):
            if len(siblings) == 1:
                return True
        return False

    def setFont(self, font):
        super().setFont(font)
        self.update()
        
    def parse_user_text(self):
        scene = self.scene()
        if scene:
            scene.parse_user_text(text=self)
                
        
        