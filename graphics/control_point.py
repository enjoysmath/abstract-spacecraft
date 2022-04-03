from PyQt5.QtCore import QPointF, Qt, QRectF, pyqtSignal
from core.qt_tools import Pen, SimpleBrush, set_pen_alpha, set_brush_alpha
from core.geom_tools import mag2D, closest_point_on_path, paint_selection_shape
from copy import deepcopy
from PyQt5.QtWidgets import QGraphicsObject
from PyQt5.QtGui import QPainterPath, QColor
from graphics.graphics_shape import GraphicsShape
from graphics.color_fillable import ColorFillable
from graphics.bounded import Bounded

class ControlPoint(GraphicsShape, ColorFillable, Bounded):
    default_fill_color = QColor(255,180,10,150)
    default_border_color = QColor(255,180,10,200)
    default_relative_radius = 1
    default_hide_after_seconds = 1
    default_shape_padding = 10.0
    default_bounding_rect_padding = 10.0
    control_point_diameter = 8.0
    
    position_changed = pyqtSignal(QPointF, QPointF)
    position_change_iota = pyqtSignal(QPointF)  
    mouse_double_clicked = pyqtSignal(QPointF)
    mouse_released = pyqtSignal(QPointF)
    mouse_pressed = pyqtSignal(QPointF)    
    
    def __init__(self):
        GraphicsShape.__init__(self)
        ColorFillable.__init__(self)
        Bounded.__init__(self)
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable | self.ItemSendsScenePositionChanges | \
                      self.ItemSendsGeometryChanges | self.ItemIsFocusable)
        
        self.setFlag(self.ItemSendsGeometryChanges, True)
        d = self.control_point_diameter
        self._shapePad = d/2.0
        #self.set_ignore_drag(True)
        self.setZValue(100.0)
        self._rect = QRectF(-d/2, -d/2, d, d)
        self._boundingRectPad = 2.0
        self._boundingRect = QRectF()
        self.setBrush(SimpleBrush(self.default_fill_color))
        self.setPen(Pen(self.default_border_color, 1.0))
        self.update()     
        
    def __setstate__(self, data:dict):
        self.__init__()
        self._setState(data)
        
    def __getstate__(self) -> dict:
        return self._getState({})
    
    def _setState(self, data:dict):
        self.__init__()
        GraphicsShape._setState(self, data['graphics shape'])
        ColorFillable._setState(self, data['fillable'])
        self._rect = data['rect']
        #self.setParentItem(data['parent'])
                
    def _getState(self, data:dict):
        data['graphics shape'] = GraphicsShape._getState(self, {})
        data['fillable'] = ColorFillable._getState(self, {})        
        data['rect'] = self._rect
        #data['parent'] = self.parentItem()
        return data
    
    def copy(self, obj):
        super().copy(obj)
                   
    def closest_boundary_point(self, pos):
        radius = self.radius()
        v = pos - self._rect.center()
        mag = mag2D(v)
        if abs(mag) == 0:
            return self._rect.center()
        return v / mag * radius    
    
    def __str__(self):
        return 'control point'
            
    def set_radius(self, radius):
        self._shapePad = radius
        self.update_paint()
        
    def update_paint(self):
        self._updatePaintPath()
        self._updateSelectionPath()
        #self._updateRect()
        self._updateBoundingRect()
        if self.parentItem():
            self.parentItem().update()
        
    def radius(self):
        return self._shapePad
        
    def setVisible(self, en):
        if en != self.isVisible():
            super().setVisible(en)
            
    def setPos(self, pos:QPointF):
        if pos != self.pos():
            super().setPos(pos)
            parent = self.parentItem()
            if parent:
                parent.update()
                parent.update_connectors()
            
    def _updatePaintPath(self):
        self._paintPath.clear()
        pad = self._shapePad
        self._paintPath.addEllipse(self._rect.adjusted(-pad, -pad, pad, pad))                
        
    def _updateSelectionPath(self):
        self._selectionPath.clear()
        pad = self._boundingRectPad
        rect = self._rect.adjusted(-pad, -pad, pad, pad)
        self._selectionPath.addEllipse(rect)
                
    def boundingRect(self):
        return self._boundingRect
    
    def _updateBoundingRect(self):
        pad = self._boundingRectPad + self._shapePad + self.pen.widthF() / 2
        self._boundingRect = self._rect.adjusted(-pad, -pad, pad, pad)                             
           
    def paint(self, painter, option, widget):
        if self.isSelected() and self.scene():
            paint_selection_shape(painter, self._selectionPath, self.transform(),
                                  self.transformations(), self.scene().backgroundBrush().color())
        shape = self.paint_shape()
        if shape:
            painter.setRenderHints(painter.Antialiasing | painter.HighQualityAntialiasing)    
            painter.setPen(self.pen)
            painter.setBrush(self.brush)
            painter.drawPath(shape)             
            
    def update(self):
        self._updateBoundingRect()
        self._updatePaintPath()
        self._updateSelectionPath()
        super().update()
        
    def setVisible(self, vis:bool):
        if vis != self.isVisible():
            super().setVisible(vis)